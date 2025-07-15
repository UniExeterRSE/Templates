"""Tests for the dash_app module callback registration functionality."""

import sys


class TestCallbackRegistration:
    """Tests for the callback registration functionality in dash_app using real callbacks."""

    def test_register_all_callbacks_imports_real_modules(self):
        """
        Test that register_all_callbacks imports all expected callback modules.
        """
        from src import dash_app

        # Remove any previously loaded callback modules (in correct order)
        for mod in sorted(list(sys.modules), reverse=True):
            if mod == "callbacks" or mod.startswith("callbacks."):
                sys.modules.pop(mod)

        # Run the real callback registration
        dash_app.register_all_callbacks()

        # List the expected callback module names explicitly based on the project structure
        expected_modules = [
            "callbacks.layout_callbacks",
            "callbacks.auth.login_callbacks",
            "callbacks.auth.registration_callbacks",
            "callbacks.app.select_images_callbacks",
            "callbacks.app.review_images_callbacks",
        ]

        # Assert that each expected callback module is imported
        missing = [
            modname for modname in expected_modules if modname not in sys.modules
        ]
        assert not missing, f"Expected callback modules not imported: {missing}"
