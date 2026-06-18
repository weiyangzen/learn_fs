# sources/test-tools/strace/src/print_utils.h

Purpose: Shared declarations for low-level print helpers used throughout syscall and protocol decoders.

Important APIs/types/functions: groups utility printers for scalar arrays, xlat-backed values, strings, addresses, file descriptors, IDs, and reusable field formatting macros that other files call indirectly.

Control flow: header only; it exposes helper signatures and inline/macro glue so decoders can keep bodies table-driven and concise.

State and persistence: no runtime state in the header; functions it declares may consult global output mode, xlat verbosity, and tracee context.

Dependencies/integration: sits near the core `defs.h`/`print_fields.h` layer and is used by ioctl, netlink, ptrace, time, and resource decoders.

Risks: because it is widely included, incompatible changes propagate broadly. Helper semantics around quoting, verbosity, and unavailable data must stay stable for golden-output tests.

Test signals: broad strace test-suite diffs, especially xlat verbosity, array printing, and invalid pointer cases.
