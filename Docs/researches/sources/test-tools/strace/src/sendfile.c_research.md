# sources/test-tools/strace/src/sendfile.c

Purpose: decodes `sendfile` and `sendfile64`, including in/out offset pointer updates.

Important APIs/types/functions: `SYS_FUNC(sendfile64)`, `SYS_FUNC(sendfile)`, `umove_or_printaddr`, `umoven_to_uint64_or_printaddr`, `tfetch_to_uint64`, `printfd`, and `tprint_value_changed`.

Control flow: entry prints output fd, input fd, and the initial offset pointer value if readable. If offset is unreadable or count is zero, it prints count immediately and returns decoded. Otherwise it keeps the indirect offset open and on exit prints a changed offset value when the call succeeded and returned nonzero bytes, then prints count.

State and persistence behavior: no tcb private data; the output shape is maintained by leaving the indirect print open between entry and exit.

Dependencies and integration points: uses current personality word size for legacy `sendfile` offset width and fixed 64-bit offset for `sendfile64`.

Risks: offset is optional in Linux semantics, but this decoder relies on safe address printers/fetchers. Entry/exit output balance must remain correct for zero-count, failed, and unreadable-offset cases.

Test signals: null offset, invalid offset, zero count, successful transfer changing offset, no-change transfer, 32-bit and 64-bit personalities, and fd formatting.
