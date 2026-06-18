# sources/test-tools/syzkaller/pkg/repro/strace.go

## Purpose

`strace.go` reruns an established reproducer under `strace` to collect syscall-level output and check whether the traced run hits the same bug.

## Important APIs, Types, And Control Flow

`StraceResult` contains a crash `Report`, captured `Output`, and `Error`. `RunStrace` requires `cfg.StraceBin`, leases a VM from the dispatcher, updates VM status to `running strace`, calls `instance.SetupExecProg` with `StraceBin` and a 2 MiB before-context buffer, then executes either `RunCProg` or `RunSyzProg` according to `Result.CRepro`. `straceFailed` wraps setup/run errors. `IsSameBug` compares titles between strace and repro reports while handling nils.

## State, Dependencies, Integration, Risks, And Test Signals

State is transient VM execution plus captured output. Dependencies are `instance`, `mgrconfig`, `report`, VM dispatcher, and logging. It integrates after successful reproduction and before reporting richer diagnostics. Risks include missing strace binary, strace perturbing timing-sensitive crashes, insufficient output context, setup failures, and title-only equality treating changed reports as different even if semantically related. There is no dedicated unit test in this subset; integration tests need a configured VM and strace binary.
