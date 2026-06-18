## sources/test-tools/syzkaller/pkg/kfuzztest-executor/executor.go

Purpose: Linux local executor for KFuzzTest pseudo-syscalls, bypassing the normal C++ executor by writing generated inputs to debugfs and collecting KCOV coverage.

Important APIs/types/functions: `KFuzzTestExecutor`, `Submit`, `Shutdown`, `NewKFuzzTestExecutor`, `workerLoop`, and `execKFuzzTestCallLocal`.

Control flow: constructor starts N workers. Each worker enables KCOV for its OS thread, processes queue requests, executes each call by marshalling the second argument and writing it to `/sys/kernel/debug/kfuzztest/<test>/input` under KCOV tracing, fills `flatrpc.CallInfo` with signal/cover PCs or blocked error, calls `req.Done`, and optionally sleeps cooldown.

State and persistence: job channel and waitgroup; writes to kernel debugfs input files; KCOV state per worker thread.

Dependencies and integration: implements `queue.Executor`; depends on `kcov`, `kfuzztest`, `prog.MarshallKFuzztestArg`, `flatrpc`, and `osutil.WriteFile`.

Risks: nil `req.Prog` is logged but then dereferenced. Assumes generated syscall argument layout. Requires Linux, debugfs KFuzzTest files, and KCOV permissions. Shutdown closes job channel; concurrent Submit after shutdown will panic.

Test signals: no direct tests in this file; behavior depends on KFuzzTest manager/integration runs.
