# sources/test-tools/strace/src/linux/generic/signalent.h

Purpose: maps `generic` signal numbers to printable names, with 33 slots including 0, SIGHUP, SIGINT, SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGBUS.

Important APIs/types/functions: signal-name table entries consumed by signal and sigset printers.

Control flow: signal decoders index this table when formatting signal numbers, pending masks, handlers, and signal-return state.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: signal numbering is ABI-specific; validate with signal delivery/kill traces and generated signal table comparison.

Source-read signal: reviewed complete local file (40 lines).
