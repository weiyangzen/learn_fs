# sources/test-tools/pynfs/nfs4.1/testmod.py

Purpose: generic pynfs test discovery, dependency resolution, execution, result formatting, and JSON/XML reporting engine.

Important APIs/types/functions: result constants, `Result`, `TestException` subclasses, `Test`, base `Environment`, `runtests`, `_runtree`, `_import_by_name`, `parseversions`, `createtests`, `printresults`, `json_printresults`, and `xml_printresults`.

Control flow: `createtests` imports a suite package, scans modules in `package.__all__`, wraps every callable whose name starts with `test`, parses docstring fields `FLAGS`, `DEPEND`, `CODE`, and `VERS`, creates flag bitmasks, validates unique codes, and resolves dependencies to tests or dependency functions. `runtests` walks tests and `_runtree` recursively runs dependencies, handling circular wait states, omitted tests, failed dependencies, forced/rundeps behavior, and actual `Test.run` execution.

State and persistence behavior: each `Test` stores result, timing, flags, dependencies, doc metadata, and status. Pickling strips function/dependency/flag references. Reporting functions serialize current result state to stdout, JSON, or XML.

Dependencies/integration: used by both `testclient.py` and `testserver.py`; relies on suite packages exposing `__all__`, docstring metadata discipline, `nfs4lib`, and environment lifecycle hooks.

Risks and test signals: `Result.__eq__` compares non-int results by identity, which is intentional for singleton defaults but subtle. `parseversions` error references undefined `s` in one branch. XML/JSON reporters include every test rather than only requested tests, so consumers must interpret skipped/omitted state.
