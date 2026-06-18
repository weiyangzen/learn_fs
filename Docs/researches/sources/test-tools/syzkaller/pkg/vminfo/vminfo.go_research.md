# sources/test-tools/syzkaller/pkg/vminfo/vminfo.go

## Purpose

`vminfo.go` defines the public VM-info checker. It extracts machine information from fetched VM files and checks enabled syscalls/features through a queue executor.

## Important APIs, Types, And Functions

`KernelModule`, `Checker`, and `Config` are the public core types. `New` selects OS-specific checker implementations and wraps a plain queue executor with deduplication. `MachineInfo` parses modules and formatted machine info sections. `Run` executes syscall/feature checks and maps context cancellation to `ErrAborted`. `Next` implements `queue.Source`. `filesystem` models fetched files with `ReadFile` and `ReadDir`; `nopChecker` is the default OS implementation.

## Control Flow, State, Dependencies, And Integration

Callers fetch files listed by `RequiredFiles`/`CheckFiles`, feed them into `MachineInfo` and `Run`, and drive queue requests by consuming `Checker.Next`. Persistent state is the deduplicating queue and checker config. `MachineInfo` ignores missing optional machine-info files but returns other errors.

## Risks And Test Signals

The virtual filesystem `ReadDir` does not sort, so formatted KVM output order can vary. `Run` returns `ErrAborted` after `cc.do` if context is canceled, even if partial data existed. Tests in `vminfo_test.go` cover host file shape, generic syscall support, queue request generation, and synthetic executor success.
