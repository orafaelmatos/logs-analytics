#!/usr/bin/env python3
"""
Test runner script for the Log Analytics application.
This script provides various options for running tests with different configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found. Make sure pytest is installed.")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run tests for the Log Analytics application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit            # Run only unit tests
  python run_tests.py --api             # Run only API tests
  python run_tests.py --integration     # Run only integration tests
  python run_tests.py --coverage        # Run tests with coverage report
  python run_tests.py --fast            # Run tests without coverage (faster)
  python run_tests.py --verbose         # Run tests with verbose output
  python run_tests.py --parallel        # Run tests in parallel
        """
    )
    
    parser.add_argument(
        '--unit', 
        action='store_true', 
        help='Run only unit tests'
    )
    parser.add_argument(
        '--api', 
        action='store_true', 
        help='Run only API tests'
    )
    parser.add_argument(
        '--integration', 
        action='store_true', 
        help='Run only integration tests'
    )
    parser.add_argument(
        '--database', 
        action='store_true', 
        help='Run only database tests'
    )
    parser.add_argument(
        '--celery', 
        action='store_true', 
        help='Run only Celery tests'
    )
    parser.add_argument(
        '--coverage', 
        action='store_true', 
        help='Run tests with coverage report'
    )
    parser.add_argument(
        '--fast', 
        action='store_true', 
        help='Run tests without coverage (faster)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Run tests with verbose output'
    )
    parser.add_argument(
        '--parallel', 
        action='store_true', 
        help='Run tests in parallel (requires pytest-xdist)'
    )
    parser.add_argument(
        '--watch', 
        action='store_true', 
        help='Run tests in watch mode (requires pytest-watch)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Run tests with debug output'
    )
    parser.add_argument(
        '--k', 
        type=str, 
        help='Only run tests matching the given substring expression'
    )
    parser.add_argument(
        '--m', 
        type=str, 
        help='Only run tests matching given mark expression'
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test selection
    if args.unit:
        cmd.extend(['-m', 'unit'])
    elif args.api:
        cmd.extend(['-m', 'api'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.database:
        cmd.extend(['-m', 'database'])
    elif args.celery:
        cmd.extend(['-m', 'celery'])
    
    # Add coverage options
    if args.coverage:
        cmd.extend(['--cov=backend', '--cov-report=html', '--cov-report=term-missing'])
    elif args.fast:
        cmd.extend(['--no-cov'])
    
    # Add output options
    if args.verbose:
        cmd.extend(['-v', '-s'])
    if args.debug:
        cmd.extend(['-v', '-s', '--tb=long'])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    # Add watch mode
    if args.watch:
        cmd.extend(['--pdb'])
    
    # Add test filtering
    if args.k:
        cmd.extend(['-k', args.k])
    if args.m:
        cmd.extend(['-m', args.m])
    
    # Add test directory
    cmd.append('tests/')
    
    # Run the tests
    success = run_command(cmd, "Test Suite")
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
