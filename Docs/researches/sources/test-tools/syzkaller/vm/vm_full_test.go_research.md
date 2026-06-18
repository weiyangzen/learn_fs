# sources/test-tools/syzkaller/vm/vm_full_test.go

Purpose: integration-style unit test for repeated `Instance.Run` calls through the real `vmimpl.Multiplex` path without requiring an external VM.

Important APIs/types/functions: `localInstancePool`, `localInstance`, `makeLocalInstance`, `localInstance.Run`, init-time `vmimpl.Register("test-local")`, and `TestMultipleRun`.

Control flow: the local backend creates an `OutputMerger`, splits the requested command into executable/args, runs it in the instance workdir with stdout/stderr pipes, and uses `vmimpl.Multiplex`. `TestMultipleRun` creates a Linux/AMD64 syzkaller VM wrapper using the local backend and runs `echo Hello` three times with `ExitNormal`, checking that each run returns exactly `Hello\n`.

State and persistence: test state is a temporary workdir, local process pipes, and merger goroutines. No guest or persistent external state is created.

Dependencies and integration: depends on `osutil.LongPipe`, `osutil.Command`, `vmimpl.OutputMerger`, `vmimpl.Multiplex`, generic `vm.Run`, and the helper `makeLinuxAMD64Futex` from `vm_test.go`.

Risks: command parsing uses `strings.Split`, so it is only suitable for simple test commands; `Copy` and `Forward` are stubs; this test exercises command lifecycle but not crash parsing.

Test signals: verifies that a single instance can be reused for multiple runs and that merger state remains usable across sequential command executions.
