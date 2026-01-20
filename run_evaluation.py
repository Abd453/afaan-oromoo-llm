#!/usr/bin/env python3
"""
Evaluation Runner for Afaan Oromo LLM System

Usage:
    python run_evaluation.py                    # Run all tests
    python run_evaluation.py --category cultural # Run specific category
    python run_evaluation.py --report-html      # Generate HTML report
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from evaluation.evaluation import run_evaluation_suite
from llm_client import query_llm


def load_test_cases(test_file: str = "evaluation/test_cases.json") -> list:
    """Load test cases from JSON file."""
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_cases']


def filter_by_category(test_cases: list, category: str) -> list:
    """Filter test cases by category."""
    if not category:
        return test_cases
    return [tc for tc in test_cases if tc.get('category') == category]


def generate_html_report(results_data: dict, output_file: str):
    """Generate HTML report from evaluation results."""
    summary = results_data['summary']
    results = results_data['results']
    
    # Group results by category
    by_category = {}
    for result in results:
        test_case = result
        category = test_case.get('category', 'unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(result)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Afaan Oromo LLM Evaluation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .category-section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .test-result {{
            border-left: 4px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            background: #f9f9f9;
        }}
        .test-result.pass {{
            border-left-color: #4caf50;
        }}
        .test-result.fail {{
            border-left-color: #f44336;
        }}
        .test-id {{
            font-weight: bold;
            color: #333;
        }}
        .test-input {{
            color: #555;
            font-style: italic;
            margin: 5px 0;
        }}
        .test-response {{
            background: white;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 0.9em;
            max-height: 200px;
            overflow-y: auto;
        }}
        .metrics {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}
        .metric-badge {{
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        .pass-badge {{
            background: #4caf50;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .fail-badge {{
            background: #f44336;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .notes {{
            color: #f44336;
            margin-top: 5px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Afaan Oromo LLM Evaluation Report</h1>
        <p>Generated: {summary['timestamp']}</p>
    </div>
    
    <div class="summary">
        <div class="metric-card">
            <div class="metric-value">{summary['total_tests']}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['passed']}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['failed']}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['pass_rate']:.1%}</div>
            <div class="metric-label">Pass Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['avg_response_time']:.2f}s</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary['avg_oromo_ratio']:.0%}</div>
            <div class="metric-label">Avg Oromo Content</div>
        </div>
    </div>
"""
    
    # Add results by category
    for category, cat_results in by_category.items():
        passed = sum(1 for r in cat_results if r['passed'])
        total = len(cat_results)
        
        html += f"""
    <div class="category-section">
        <div class="category-title">{category.replace('_', ' ').title()} ({passed}/{total} passed)</div>
"""
        
        for result in cat_results:
            status_class = 'pass' if result['passed'] else 'fail'
            status_badge = f'<span class="pass-badge">✓ PASS</span>' if result['passed'] else f'<span class="fail-badge">✗ FAIL</span>'
            
            metrics = result['metrics']
            
            html += f"""
        <div class="test-result {status_class}">
            <div>
                <span class="test-id">{result['test_id']}</span>
                {status_badge}
            </div>
            <div class="test-input">Input: {result['input_text'][:100]}...</div>
            <div class="test-response">{result['actual_response'][:300]}...</div>
            <div class="metrics">
                <span class="metric-badge">⏱ {metrics['response_time']:.2f}s</span>
                <span class="metric-badge">🗣 Oromo: {metrics['language_consistency']:.0%}</span>
                <span class="metric-badge">📏 {metrics['response_length']} chars</span>
                <span class="metric-badge">🎭 {metrics['cultural_markers']} cultural markers</span>
            </div>
            {f'<div class="notes">⚠ {result["notes"]}</div>' if not result['passed'] else ''}
        </div>
"""
        
        html += "    </div>\n"
    
    html += """
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Run evaluation suite for Afaan Oromo LLM'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Filter tests by category (e.g., cultural, technical, greetings)'
    )
    parser.add_argument(
        '--test-file',
        type=str,
        default='evaluation/test_cases.json',
        help='Path to test cases JSON file'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )
    parser.add_argument(
        '--report-html',
        action='store_true',
        help='Generate HTML report in addition to JSON'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='evaluation/results',
        help='Directory to save results'
    )
    
    args = parser.parse_args()
    
    # Load test cases
    print("Loading test cases...")
    try:
        test_cases = load_test_cases(args.test_file)
    except FileNotFoundError:
        print(f"❌ Error: Test file not found: {args.test_file}")
        return 1
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in test file: {args.test_file}")
        return 1
    
    # Filter by category if specified
    if args.category:
        test_cases = filter_by_category(test_cases, args.category)
        if not test_cases:
            print(f"❌ Error: No test cases found for category: {args.category}")
            return 1
        print(f"Running {len(test_cases)} tests from category: {args.category}")
    else:
        print(f"Running all {len(test_cases)} test cases")
    
    # Run evaluation
    results_data = run_evaluation_suite(
        test_cases=test_cases,
        query_func=query_llm,
        save_results=not args.no_save,
        results_dir=args.results_dir
    )
    
    # Generate HTML report if requested
    if args.report_html:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = f"{args.results_dir}/evaluation_{timestamp_str}.html"
        generate_html_report(results_data, html_file)
    
    # Return exit code based on pass rate
    pass_rate = results_data['summary']['pass_rate']
    if pass_rate >= 0.8:
        print("\n✓ Evaluation PASSED (≥80% pass rate)")
        return 0
    else:
        print(f"\n✗ Evaluation FAILED ({pass_rate:.1%} pass rate < 80%)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

