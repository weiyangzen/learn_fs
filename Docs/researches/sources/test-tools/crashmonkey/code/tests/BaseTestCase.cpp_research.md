# sources/test-tools/crashmonkey/code/tests/BaseTestCase.cpp

Purpose: implements common initialization and tracked workload execution for dynamically loaded CrashMonkey test cases.

Important APIs/functions: `init_values()` stores mount directory and filesystem size. `Run()` selects recording wrappers for checkpoint `0` and passthrough wrappers for later checkpoint-specific reruns, calls the subclass `run(checkpoint)`, and serializes recorded filesystem modifications to `change_fd` on the full run.

Control flow and state: during the first workload execution, `cm_` points to `RecordCmFsOps`, so user-tool operations are recorded. During checkpoint reruns, `cm_` points to `PassthroughCmFsOps`, avoiding duplicate modification logging. Subclasses call `cm_` or direct POSIX APIs in `run()`.

Dependencies and integration: depends on `user_tools/api/wrapper.h` types `DefaultFsFns`, `RecordCmFsOps`, and `PassthroughCmFsOps`. `Tester::test_run()` calls `Run()`.

Risks: `cm_` points to stack objects inside `Run()`, so subclasses must not retain it after `run()` returns. Direct calls to global helpers like `Checkpoint()` bypass `cm_` and may not be recorded consistently. Serialization is skipped for checkpoint reruns by design.

Test signals: a mock subclass can verify that checkpoint `0` serializes changes and checkpoint `>0` does not.
