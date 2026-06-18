<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py

Purpose: Vendored `discover` 0.4.0 backport of unittest discovery for older Python versions, exposing a `DiscoveringTestLoader`, CLI `main`, default loader, and setup.py collector.

Important APIs/functions: `DiscoveringTestLoader` implements `loadTestsFromTestCase`, `loadTestsFromModule`, `loadTestsFromName(s)`, `getTestCaseNames`, `discover`, `_get_name_from_path`, `_get_module_from_name`, `_match_path`, and `_find_tests`. Failure helpers create synthetic failing test cases for import/load failures. `_CmpToKey` adapts legacy `cmp` sorting. `relpath` fallback supports Python versions without `os.path.relpath`. `_do_discovery`, `_run_tests`, `main`, `defaultTestLoader`, and `collector` provide CLI and setup integration.

Control flow: `discover` normalizes top-level and start directories, ensures the top-level directory is on `sys.path`, validates importability, then calls `_find_tests`. `_find_tests` scans files matching valid module names and the pattern, imports modules by derived dotted name, rejects globally installed shadow imports by comparing module paths, loads tests, and recurses only into packages containing `__init__.py`. Package-level `load_tests` can override recursion.

State and persistence behavior: No durable persistence. It mutates `sys.path`, stores `_top_level_dir` on the loader instance, imports modules into `sys.modules`, and can call arbitrary module-level import code during discovery.

Dependencies and integration points: Uses `unittest`, `optparse`, `fnmatch`, `types`, `traceback`, and filesystem APIs. It supports old Python compatibility required by the vendored test stack and exposes a console script through setup metadata.

Risks: Importing tests has side effects. Directory listing order is not sorted before discovery, though method names are sorted, so module discovery order can vary by filesystem. The compatibility code targets very old Python versions and uses broad `except` clauses to synthesize failures. `sys.path.remove(top_level_dir)` in dotted-module discovery assumes that exact entry was inserted and still exists.

Test signals: Self-tests should exercise discovery from directories and dotted names, pattern filtering, package `load_tests`, failed imports producing failing tests, top-level path validation, and CLI exit status. The package's `setup.py` declares `discover.collector` as its test suite.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py -->
