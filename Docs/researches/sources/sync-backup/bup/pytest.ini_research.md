## sources/sync-backup/bup/pytest.ini

Purpose: pytest configuration for Bup’s test suite.

Important content: declares `testpaths = test/int test/ext`, and registers the `release` marker. It intentionally does not set `addopts`; the `./pytest` wrapper owns defaults.

State, dependencies, and risks: no runtime state. Test discovery depends on `test/ext/conftest.py` for non-Python executable tests. Running plain `pytest` without the wrapper will not get the wrapper’s default arguments or environment.
