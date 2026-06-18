<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/testmod.py -->
# sources/test-tools/pynfs/nfs4.0/lib/testmod.py

Purpose: pynfs test-suite runner and reporting framework. It discovers test functions, parses docstring metadata, resolves dependencies/flags/version ranges, runs tests in dependency order, records outcomes, and emits text, JSON, and XML reports.

Important APIs/types/functions: outcome constants model not-run/running/wait/omit/fail/unsupported/warn/pass. `Result` stores outcome, message, traceback, and default marker. `Test` wraps one test function, parses `FLAGS`, `DEPEND`, `CODE`, and `VERS`, formats display output, provides `fail()`, `fail_support()`, `pass_warn()`, and runs environment lifecycle hooks. `Environment` is a base hook class. `runtests()` and `_runtree()` resolve dependencies recursively. `createtests()` imports package modules from `__all__`, finds `test*` functions, validates unique codes, builds flag bitmasks, and resolves dependencies. `printresults()`, `json_printresults()`, and `xml_printresults()` summarize results.

Control flow/state: each `Test` transitions through `TEST_WAIT`, run/omit/fail/pass states, and stores elapsed time. Dependencies can be other tests or callable dependency functions marked `DEP_FUNCT`. Environment startup/shutdown runs around each test, with cleanup of sessions/clients after success.

Dependencies/integration: imports `nfs4lib`, Python import/introspection, traceback formatting, JSON, and DOM XML. It is used by pynfs command-line runners to turn suite modules into executable tests.

Risks/test signals: duplicate `def _run_filter` text appears in the file and would be a syntax error in the shown source if not otherwise patched; this is a critical import-time risk. Docstring metadata is mandatory for codes and fragile under renamed tests. Report outputs are the suite-level test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/testmod.py -->
