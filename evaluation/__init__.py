"""Evaluation framework for Afaan Oromo LLM system."""
from .evaluation import (
    evaluate_response,
    run_evaluation_suite,
    calculate_language_consistency,
    measure_response_time,
    EvaluationMetrics,
    EvaluationResult
)

__all__ = [
    'evaluate_response',
    'run_evaluation_suite',
    'calculate_language_consistency',
    'measure_response_time',
    'EvaluationMetrics',
    'EvaluationResult'
]

