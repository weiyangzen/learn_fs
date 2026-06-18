# sources/test-tools/crashmonkey/code/tests/BaseTestCase.h

Purpose: declares the abstract interface all dynamically loaded CrashMonkey test cases implement.

Important APIs/types: subclasses implement `setup()`, `run(checkpoint)`, and `check_test(last_checkpoint, DataTestResult*)`. `Run()` is the non-virtual wrapper around `run()`. `init_values()` injects mount dir and filesystem size. Factory typedefs define shared-object symbols.

Control flow and integration: `ClassLoader` loads `test_case_get_instance` and `test_case_delete_instance`; `c_harness.cpp` invokes setup/run/check through `Tester`.

State: protected `mnt_dir_`, `filesys_size_`, and `cm_` are available to tests.

Risks: raw pointer `cm_` has temporary lifetime during `Run()`. The interface mixes direct POSIX tests and user-tool-recorded tests, so test authors must understand when to use `cm_`.

Test signals: every `.so` test must export the factory symbols and behave correctly for checkpoint `0` plus checkpoint-specific reruns.
