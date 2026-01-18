import random
from typing import List, Optional, Set
import structlog

from ..config.settings import Settings


logger = structlog.get_logger(__name__)


class ModelSelector:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.available_models = settings.available_models.copy()
        self.failed_models: Set[str] = set()
        self.model_usage_count: dict[str, int] = {}
        
    def get_random_model(self, exclude_models: Optional[List[str]] = None) -> str:
        exclude_models = exclude_models or []
        
        if not self.settings.enable_model_rotation:
            return self.available_models[0]
            
        eligible_models = [
            model for model in self.available_models
            if model not in exclude_models and model not in self.failed_models
        ]
        
        if not eligible_models:
            logger.warning(
                "No eligible models available, clearing failed models and retrying",
                failed_models=list(self.failed_models),
                exclude_models=exclude_models
            )
            self.failed_models.clear()
            eligible_models = [
                model for model in self.available_models
                if model not in exclude_models
            ]
            
        if not eligible_models:
            logger.error(
                "No models available after clearing failures",
                total_models=len(self.available_models),
                exclude_models=exclude_models
            )
            raise RuntimeError("No available models to use")
            
        selected_model = random.choice(eligible_models)
        self.model_usage_count[selected_model] = self.model_usage_count.get(selected_model, 0) + 1
        
        logger.info(
            "Selected random model",
            model=selected_model,
            total_usage=self.model_usage_count[selected_model],
            eligible_count=len(eligible_models)
        )
        
        return selected_model
    
    def mark_model_failed(self, model: str, error: Exception):
        self.failed_models.add(model)
        logger.warning(
            "Marked model as failed",
            model=model,
            error=str(error),
            total_failed=len(self.failed_models)
        )
    
    def get_model_for_retry(self, used_models: List[str]) -> Optional[str]:
        if len(used_models) >= self.settings.max_retry_attempts:
            logger.warning(
                "Max retry attempts reached",
                max_attempts=self.settings.max_retry_attempts,
                used_models=used_models
            )
            return None
            
        try:
            return self.get_random_model(exclude_models=used_models)
        except RuntimeError:
            logger.error(
                "No models available for retry",
                used_models=used_models,
                failed_models=list(self.failed_models)
            )
            return None
    
    def get_usage_stats(self) -> dict:
        return {
            "model_usage_count": self.model_usage_count.copy(),
            "failed_models": list(self.failed_models),
            "total_models": len(self.available_models),
            "available_models": len([
                m for m in self.available_models 
                if m not in self.failed_models
            ])
        }
    
    def reset_failed_models(self):
        self.failed_models.clear()
        logger.info("Reset all failed models")