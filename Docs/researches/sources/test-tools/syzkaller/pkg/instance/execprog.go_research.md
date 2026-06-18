## sources/test-tools/syzkaller/pkg/instance/execprog.go

Purpose: wraps a VM instance with syz-execprog/syz-executor setup and helpers to run syzkaller programs, compiled C reproducers, arbitrary binaries, coverage collection, strace, crash report parsing, and optional memory dump extraction.

Important APIs/types/functions: `ExecProgInstance`, `OptionalConfig`, `RunResult`, `RunOptions`, `SetupExecProg`, `CreateExecProgInstance`, `RunCProg`, `RunCProgRaw`, `RunSyzProgFile`, `RunSyzProg`, `parseCoverageFile`, and `runStreamAndCollectStdout`.

Control flow: setup copies binaries unless target paths are preconfigured. `runCommand` optionally prefixes command with strace, applies context timeout and VM exit conditions, parses/symbolizes reports, and extracts dumps for panics. Syz program execution writes/copies program files, builds `ExecprogCmd`, optionally parses sorted cover files, and returns output/report/coverage. C execution builds locally, copies binary, and runs with broader exit conditions. Streaming helper drains stdout safely and cancels on writer/context errors to avoid VM channel deadlocks.

State and persistence: creates temp syz program files, cover directories, compiled binaries, and optional dump files. VM-side copied binaries/files are transient to the VM. No durable package state.

Dependencies and integration: central integration point for `vm`, `report`, `mgrconfig`, `csource`, `prog`, `targets`, and `osutil`. `dump.go` depends on `runStreamAndCollectStdout`.

Risks: command strings are assembled manually and depend on option escaping/paths. Coverage parsing assumes hex one-PC-per-line files. Timeout is converted to output text and not treated as infrastructure error. Stream helper warns that the VM must not be reused after error because output may be incomplete.

Test signals: `execprog_test.go` heavily tests stream draining/cancellation/error cases; `instance_test.go` tests `ExecprogCmd` formatting.
