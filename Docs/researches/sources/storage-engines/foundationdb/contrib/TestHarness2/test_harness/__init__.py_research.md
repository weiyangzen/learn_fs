# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/__init__.py

Purpose: package marker for the TestHarness2 Python module. It intentionally contains no runtime code.

Important APIs and control flow: none; import side effects are absent.

State and persistence: none.

Dependencies and integration: enables `python3 -m test_harness.app` and sibling module imports from Joshua scripts.

Risks and test signals: packaging/import path issues surface as `ModuleNotFoundError` in wrappers. A basic import smoke test is sufficient.
