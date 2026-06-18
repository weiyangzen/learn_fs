# sources/test-tools/lcov/tests/bin/checkdeps

Purpose: Perl dependency preflight helper for test scripts. It scans shebang Perl files for simple `use Module;` directives and verifies that required modules can be loaded.

Important APIs: executable `checkdeps <perl-file1> ...`. Helper `check_file($file)` returns nonzero if required modules are missing; `main` aggregates across all paths.

Control flow and state: for each file, it reads the first line and only scans files whose shebang mentions Perl. It then scans later lines matching `use <module> ...;`, skips repository-local modules such as `lcovutil`, `annotateutil`, `gitversion`, `gitblame`, `getp4version`, and `p4annotate`, and runs `eval("require $module")`. Missing modules emit warnings and set return code.

Dependencies and integration: invoked by `common.mak` `checkdeps` over lcov binaries and test helpers before running tests.

Risks and test signals: only catches straightforward static `use` lines and can mis-handle import arguments or conditional dependencies. `eval` with module text parsed from source is acceptable in trusted test code but not general-purpose safe. Test signal is early failure when a developer machine lacks required Perl modules.
