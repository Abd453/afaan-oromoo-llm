"""
Evaluation module for Afaan Oromo Conversational AI System.
Provides metrics and scoring functions for assessing system performance.
"""

import json
import time
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import statistics


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    language_consistency: float  # % of Afaan Oromo content
    response_time: float  # seconds
    error_occurred: bool
    response_length: int  # character count
    contains_code: bool
    cultural_markers: int  # count of cultural references
    
    def to_dict(self):
        return asdict(self)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a single test case."""
    test_id: str
    input_text: str
    expected_type: str
    actual_response: str
    metrics: EvaluationMetrics
    passed: bool
    notes: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        result = asdict(self)
        result['metrics'] = self.metrics.to_dict()
        return result


# Afaan Oromo common words/patterns for language detection
OROMO_KEYWORDS = [
    'akkam', 'maal', 'maalif', 'eessa', 'yoom', 'akkamitti', 'eenyu',
    'gaaffii', 'deebii', 'gargaarsa', 'maaloo', 'galata', 'dhugaa',
    'jirta', 'jirtu', 'jira', 'nan', 'dha', 'tti', 'keessa', 'irraa',
    'waliin', 'guddaa', 'xiqqaa', 'haaraa', 'dullooma', 'barbaada'
]

OROMO_CULTURAL_MARKERS = [
    'irreecha', 'odaa', 'gada', 'abbaa', 'gadaa', 'oromia', 
    'oromoo', 'afaan', 'aadaa', 'seera', 'qabeenyaa'
]


def calculate_language_consistency(text: str) -> float:
    """
    Calculate percentage of Afaan Oromo content in response.
    
    Args:
        text: Response text to analyze
        
    Returns:
        Float between 0 and 1 representing Oromo language consistency
    """
    if not text or len(text.strip()) == 0:
        return 0.0
    
    # Normalize text
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    if not words:
        return 0.0
    
    # Count Oromo keywords
    oromo_word_count = sum(1 for word in words if word in OROMO_KEYWORDS)
    
    # Check for Oromo-specific characters and patterns
    has_oromo_chars = bool(re.search(r'[qxc]\w', text_lower))  # Common in Oromo
    
    # Calculate ratio
    keyword_ratio = oromo_word_count / len(words)
    
    # Boost score if Oromo-specific characters present
    if has_oromo_chars:
        keyword_ratio = min(1.0, keyword_ratio * 1.2)
    
    return round(keyword_ratio, 3)


def count_cultural_markers(text: str) -> int:
    """Count Oromo cultural references in text."""
    text_lower = text.lower()
    count = sum(1 for marker in OROMO_CULTURAL_MARKERS if marker in text_lower)
    return count


def detect_code_blocks(text: str) -> bool:
    """Check if response contains code blocks."""
    code_indicators = [
        '```', 'def ', 'class ', 'import ', 'function',
        'for(', 'while(', 'if(', '{', '}'
    ]
    return any(indicator in text for indicator in code_indicators)


def measure_response_time(func, *args, **kwargs) -> tuple:
    """
    Measure execution time of a function.
    
    Returns:
        Tuple of (result, elapsed_time_in_seconds)
    """
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def evaluate_response(
    test_case: Dict[str, Any],
    actual_response: str,
    response_time: float,
    error: Optional[str] = None
) -> EvaluationResult:
    """
    Evaluate a single response against expected criteria.
    
    Args:
        test_case: Test case dictionary with input, expected_type, etc.
        actual_response: The actual model response
        response_time: Time taken to generate response
        error: Error message if any occurred
        
    Returns:
        EvaluationResult object
    """
    test_id = test_case.get('id', 'unknown')
    input_text = test_case.get('input', '')
    expected_type = test_case.get('expected_type', '')
    validation_rules = test_case.get('validation', {})
    
    # Calculate metrics
    language_consistency = calculate_language_consistency(actual_response)
    response_length = len(actual_response)
    contains_code = detect_code_blocks(actual_response)
    cultural_markers = count_cultural_markers(actual_response)
    error_occurred = error is not None
    
    metrics = EvaluationMetrics(
        language_consistency=language_consistency,
        response_time=response_time,
        error_occurred=error_occurred,
        response_length=response_length,
        contains_code=contains_code,
        cultural_markers=cultural_markers
    )
    
    # Determine if test passed
    passed = True
    notes = []
    
    # Check validation rules
    if validation_rules:
        min_length = validation_rules.get('min_length', 10)
        max_time = validation_rules.get('max_response_time', 5.0)
        min_oromo = validation_rules.get('min_oromo_ratio', 0.1)
        must_not_error = validation_rules.get('must_not_error', True)
        
        if response_length < min_length:
            passed = False
            notes.append(f"Response too short: {response_length} < {min_length}")
        
        if response_time > max_time:
            passed = False
            notes.append(f"Response too slow: {response_time:.2f}s > {max_time}s")
        
        if language_consistency < min_oromo:
            passed = False
            notes.append(f"Low Oromo content: {language_consistency:.2f} < {min_oromo}")
        
        if must_not_error and error_occurred:
            passed = False
            notes.append(f"Error occurred: {error}")
    
    # Type-specific validation
    if expected_type == 'greeting_response':
        if not any(word in actual_response.lower() for word in ['nagaa', 'fayyaa', 'gaarii', 'gammade']):
            notes.append("Missing typical greeting response words")
    
    elif expected_type == 'technical_explanation':
        if response_length < 50:
            notes.append("Technical explanation seems too brief")
    
    elif expected_type == 'cultural_knowledge':
        if cultural_markers == 0:
            notes.append("No cultural markers found in cultural question")
    
    result = EvaluationResult(
        test_id=test_id,
        input_text=input_text,
        expected_type=expected_type,
        actual_response=actual_response if not error else f"ERROR: {error}",
        metrics=metrics,
        passed=passed,
        notes=" | ".join(notes) if notes else "All checks passed"
    )
    
    return result


def run_evaluation_suite(
    test_cases: List[Dict[str, Any]],
    query_func,
    save_results: bool = True,
    results_dir: str = "evaluation/results"
) -> Dict[str, Any]:
    """
    Run complete evaluation suite on all test cases.
    
    Args:
        test_cases: List of test case dictionaries
        query_func: Function to call for getting responses (e.g., llm_client.query_llm)
        save_results: Whether to save results to file
        results_dir: Directory to save results
        
    Returns:
        Dictionary with summary statistics and individual results
    """
    results = []
    errors = []
    
    print(f"\n{'='*60}")
    print(f"Running Evaluation Suite - {len(test_cases)} test cases")
    print(f"{'='*60}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        test_id = test_case.get('id', f'test_{i}')
        input_text = test_case.get('input', '')
        
        print(f"[{i}/{len(test_cases)}] Testing: {test_id}")
        print(f"  Input: {input_text[:50]}...")
        
        try:
            # Execute query with timing
            start_time = time.time()
            response = query_func(input_text, history_input=[])
            elapsed = time.time() - start_time
            
            # Evaluate response
            result = evaluate_response(test_case, response, elapsed)
            results.append(result)
            
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"  {status} ({elapsed:.2f}s, Oromo: {result.metrics.language_consistency:.0%})")
            
            if not result.passed:
                print(f"  Notes: {result.notes}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"  [ERROR]: {error_msg}")
            
            result = evaluate_response(
                test_case,
                "",
                0.0,
                error=error_msg
            )
            results.append(result)
            errors.append({'test_id': test_id, 'error': error_msg})
        
        print()
    
    # Calculate summary statistics
    passed_tests = [r for r in results if r.passed]
    failed_tests = [r for r in results if not r.passed]
    
    response_times = [r.metrics.response_time for r in results if r.metrics.response_time > 0]
    oromo_ratios = [r.metrics.language_consistency for r in results]
    
    summary = {
        'total_tests': len(test_cases),
        'passed': len(passed_tests),
        'failed': len(failed_tests),
        'error_count': len([r for r in results if r.metrics.error_occurred]),
        'pass_rate': len(passed_tests) / len(test_cases) if test_cases else 0,
        'avg_response_time': statistics.mean(response_times) if response_times else 0,
        'median_response_time': statistics.median(response_times) if response_times else 0,
        'avg_oromo_ratio': statistics.mean(oromo_ratios) if oromo_ratios else 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save results
    if save_results:
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(results_dir) / f"evaluation_{timestamp_str}.json"
        
        output_data = {
            'summary': summary,
            'results': [r.to_dict() for r in results]
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Results saved to: {results_file}")
        print(f"{'='*60}\n")
    
    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests:      {summary['total_tests']}")
    print(f"Passed:           {summary['passed']} ({summary['pass_rate']:.1%})")
    print(f"Failed:           {summary['failed']}")
    print(f"Errors:           {summary['error_count']}")
    print(f"Avg Response Time: {summary['avg_response_time']:.2f}s")
    print(f"Avg Oromo Ratio:  {summary['avg_oromo_ratio']:.1%}")
    print(f"{'='*60}\n")
    
    return {
        'summary': summary,
        'results': results,
        'errors': errors
    }

