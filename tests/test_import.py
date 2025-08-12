"""
Integration tests for the cchooks library import functionality.

Tests the main library entry point and import interface.
"""

import unittest
from io import StringIO


class TestLibraryImport(unittest.TestCase):
    """Test cases for library import functionality."""

    def test_import_hook_function(self):
        """Test that the hook function can be imported from cchooks."""
        # Test the main import pattern from requirements
        from src.hooks import hook

        # Verify the function is callable
        self.assertTrue(callable(hook))

        # Verify the function has the expected signature
        import inspect

        sig = inspect.signature(hook)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["hook_event_name", "stdin", "callback"])

    def test_import_all_exports(self):
        """Test that __all__ exports work correctly."""
        import src.hooks as hooks_module

        # Check that __all__ is defined
        self.assertTrue(hasattr(hooks_module, "__all__"))
        self.assertEqual(hooks_module.__all__, ["hook"])

        # Check that all items in __all__ are accessible
        for item in hooks_module.__all__:
            self.assertTrue(hasattr(hooks_module, item))

    def test_library_metadata(self):
        """Test that library metadata is properly defined."""
        import src.hooks as hooks_module

        # Check version information
        self.assertTrue(hasattr(hooks_module, "__version__"))
        self.assertIsInstance(hooks_module.__version__, str)
        self.assertRegex(hooks_module.__version__, r"^\d+\.\d+\.\d+$")

        # Check other metadata
        self.assertTrue(hasattr(hooks_module, "__author__"))
        self.assertTrue(hasattr(hooks_module, "__description__"))
        self.assertTrue(hasattr(hooks_module, "__license__"))

        # Verify metadata types
        self.assertIsInstance(hooks_module.__author__, str)
        self.assertIsInstance(hooks_module.__description__, str)
        self.assertIsInstance(hooks_module.__license__, str)

    def test_hook_function_integration(self):
        """Test basic integration of the hook function."""
        from src.hooks import hook

        # Test data that matches the Claude hook specification
        test_data = {
            "hook_event_name": "Stop",
            "session_id": "test-session",
            "stop_hook_active": True,
        }

        # Test callback function
        def test_callback(data):
            return f"Processed: {data['hook_event_name']}"

        # Execute the hook function
        result = hook("Stop", test_data, test_callback)

        # Verify the result
        self.assertEqual(result, "Processed: Stop")

    def test_import_error_handling(self):
        """Test that import errors are handled gracefully."""
        # This test ensures that if there are import issues, they're clear
        try:
            from src.hooks import hook  # noqa: F401

            # If we get here, the import succeeded
            self.assertTrue(True)
        except ImportError as e:
            # If there's an import error, it should be descriptive
            self.fail(f"Import failed with error: {e}")

    def test_module_docstring(self):
        """Test that the module has proper documentation."""
        import src.hooks as hooks_module

        # Check that module has a docstring
        self.assertIsNotNone(hooks_module.__doc__)
        self.assertIn("Claude Code Hooks Library", hooks_module.__doc__)
        self.assertIn("cchooks", hooks_module.__doc__)

    def test_clean_namespace(self):
        """Test that the module namespace is clean and only exports intended items."""
        import src.hooks as hooks_module

        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(hooks_module) if not attr.startswith("_")]

        # Should only have the hook function and metadata
        expected_attrs = {"hook"}  # Only the main function should be public
        actual_public_functions = {
            attr for attr in public_attrs if callable(getattr(hooks_module, attr))
        }

        self.assertEqual(actual_public_functions, expected_attrs)

    def test_hook_function_with_textio(self):
        """Test that the hook function works with TextIO input."""
        from src.hooks import hook
        import json

        # Create test data as JSON string
        test_data = {
            "hook_event_name": "Stop",
            "session_id": "test-session",
            "stop_hook_active": True,
        }
        json_data = json.dumps(test_data)

        # Create StringIO object to simulate TextIO
        stdin_stream = StringIO(json_data)

        # Test callback function
        def test_callback(data):
            return data["hook_event_name"]

        # Execute the hook function with TextIO input
        result = hook("Stop", stdin_stream, test_callback)

        # Verify the result
        self.assertEqual(result, "Stop")


if __name__ == "__main__":
    unittest.main()
