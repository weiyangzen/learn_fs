# sources/test-tools/strace/src/statfs.h

Purpose: normalized internal representation for filesystem stat data.

Important APIs/types/functions: `struct strace_statfs` fields for type, block sizes/counts, file counts, fsid, name length, fragment size, and mount flags.

Control flow: header only; fetchers fill this representation for common printers.

State and persistence behavior: none.

Dependencies and integration points: included by statfs fetch/print implementations and statfs syscall wrappers.

Risks: fields must cover old and new statfs ABI widths without loss. `f_flags` availability varies by kernel/ABI and must be handled by fetchers.

Test signals: filesystem magic, large block/file counts, fsid rendering, and statfs variants with and without flags.
