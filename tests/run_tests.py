#!/usr/bin/env python3
"""
Test runner for swim practice parser unit tests
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Discover and run all tests"""
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        success = run_all_tests()
        
        cov.stop()
        cov.save()
        
        # Print coverage report
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        return success
    except ImportError:
        print("Coverage not available, running tests without coverage")
        return run_all_tests()

def run_specific_test(test_name):
    """Run a specific test module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--coverage':
            # Run all tests with coverage
            success = run_tests_with_coverage()
        else:
            # Run specific test
            test_name = sys.argv[1]
            success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
