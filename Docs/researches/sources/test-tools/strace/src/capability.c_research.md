<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/capability.c -->
## sources/test-tools/strace/src/capability.c

Purpose: Decodes `capget` and `capset` syscall headers and capability bitsets.

Important APIs and types: Local `struct user_cap_header_struct`, `struct user_cap_data_struct`, `get_cap_header`, `print_cap_header`, `print_cap_bits`, `print_cap_data`, `SYS_FUNC(capget)`, and `SYS_FUNC(capset)`.

Control flow: `get_cap_header` fetches the header only when the pointer is non-null and verbose mode is active. `capget` prints header on entry and, on successful exit, decodes `datap` according to header version. `capset` prints both header and input data on entry. Version 1 uses one capability word; versions 2 and 3 use two.

State and persistence: `get_cap_header` returns a pointer to a static header buffer; it is reused across calls, so callers consume it immediately.

Dependencies and integration: Includes `caps0.h` and `caps1.h` to build enum values, then `xlat/cap_mask0.h`, `xlat/cap_mask1.h`, and `xlat/cap_version.h`. Uses pid translation printing for header pid.

Risks: Static header storage is simple but non-reentrant. Unknown capability versions are treated as one-word data, which may be incomplete for future versions.

Test signals: Tests should cover all three capability versions, null pointers, unreadable pointers, high capability bits, capget errors, and pid rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/capability.c -->
