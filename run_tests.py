#!/usr/bin/env python
"""
Simple test runner for TelepromptSDK.
"""

import sys
import unittest

if __name__ == "__main__":
    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover("tests")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())
