# sources/test-tools/strace/src/linux/arm/syscallent.h

Purpose: defines syscall table metadata for the `arm` personality, covering 405 named entries across 443 source lines; early entries include restart_syscall, exit, fork, read, write, open, close, waitpid.

Important APIs/types/functions: table initializers map syscall numbers to argument counts, trace flags, `SEN(...)` decoder handlers, and printable names. Flags observed here include CC, NF, PU, SI, TC, TCL, TD, TF, TFSF, TFST, TI, TLST.

Control flow: strace indexes this array after `arch_get_scno` and optional syscall-number shuffling, then dispatches the selected `SEN` decoder and applies table flags to path, fd, network, signal, process, stat, memory, IPC, and pure-call formatting behavior.

State/persistence behavior: compile-time dispatch metadata only; runtime state lives in `struct tcb` fields populated from registers and syscall arguments.

Dependencies/integration: depends on decoder symbols declared elsewhere in strace, architecture syscall numbering, generated common tables, and personality selection.

Risks/test signals: off-by-one numbering, stale ABI entries, or wrong flags produce incorrect syscall names/argument classes; test with known syscall-number traces, generated table checks, and cross-architecture comparison against Linux syscall headers.

Source-read signal: reviewed complete local file (443 lines).
