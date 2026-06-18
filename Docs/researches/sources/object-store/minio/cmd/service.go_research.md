# sources/object-store/minio/cmd/service.go

Purpose: This file defines service-level control signals and process control helpers used for restart, stop, reload/freezing operations, and global shutdown cancellation. It also implements the request-freeze mechanism used during synchronized boot.

Important APIs and types: `serviceSignal` enumerates `serviceRestart`, `serviceStop`, `serviceReloadDynamic`, `serviceFreeze`, and `serviceUnFreeze`. `globalServiceSignalCh` carries service commands. `GlobalContext` and `cancelGlobalContext` represent process-wide lifetime. `restartProcess` replaces or reruns the current process. `freezeServices` and `unfreezeServices` manage `globalServiceFreeze`, `globalServiceFreezeCnt`, and `globalServiceFreezeMu`.

Control flow: `restartProcess` on Windows starts a child process with the same args/env/stdio and exits only on success; on other systems it resolves the original executable with `exec.LookPath` and calls `syscall.Exec` with the same args/env, preserving PID where possible. `freezeServices` increments a counter and creates a channel on the first freeze. `unfreezeServices` decrements the counter and closes/swaps out the freeze channel when the count reaches zero.

State and persistence behavior: There is no persistence. Runtime state includes the process-wide context, service signal channel, and freeze counter/channel. `restartProcess` mutates process identity and exits/replaces the current process.

Dependencies and integration points: `signals.go` consumes `globalServiceSignalCh` and calls `restartProcess`. HTTP request handling elsewhere checks `globalServiceFreeze` to block S3 APIs during boot or administrative freeze. The file depends on Go `os/exec`, `syscall`, runtime OS checks, and MinIO's safe-close helper.

Risks: Freeze/unfreeze is reference-counted; unmatched calls can leave services frozen or prematurely unfreeze. Process restart behavior differs substantially between Windows and Unix. `GlobalContext` is package global and must be reset carefully in tests that simulate server lifecycles.

Test signals: No direct tests in this subset. Indirect signals include sync-boot freeze/unfreeze behavior during startup and signal/restart handling through `signals.go`.
