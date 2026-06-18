# sources/test-tools/strace/src/sync_file_range2.c

Purpose: decoder for architectures whose `sync_file_range2` puts flags before 64-bit range arguments.

Important APIs/types/functions: `SYS_FUNC(sync_file_range2)`, `printfd`, `printflags`, `print_arg_lld`, and `sync_file_range_flags`.

Control flow: prints fd and flags from argument 1, then decodes `offset` starting at argument 2 and `nbytes` from the returned next index.

State and persistence behavior: stateless decoder.

Dependencies and integration points: syscall table selects this variant for affected ABIs; shares xlats and print helpers with `sync_file_range.c`.

Risks: using the wrong decoder for an ABI would swap flags/range interpretation; tests must cover architecture-specific syscall tables.

Test signals: same as `sync_file_range`, plus verification that argument ordering matches the target architecture.
