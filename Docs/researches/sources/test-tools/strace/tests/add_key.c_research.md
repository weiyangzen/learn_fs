<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/add_key.c -->
## sources/test-tools/strace/tests/add_key.c

Purpose: Exhaustive combinatorial decoder test for `add_key` string, payload, length, and keyring arguments.

Important APIs/types/functions: Defines `print_val_str`, `do_add_key`, uses `tail_memdup`, `ARG_STR`, `STRINGIFY`, `KEY_SPEC_THREAD_KEYRING`, and `syscall(__NR_add_key, ...)`.

Control flow: Builds arrays of type strings, descriptions, payload pointers/lengths, and keyring ids, including NULL, invalid tail pointers, unterminated buffers, escaped strings, long strings, and known keyring constants. Nested loops invoke `do_add_key` for every combination and print the expected decoder representation.

State and persistence: Allocates tail buffers for bogus unterminated data; does not persist keys because most calls are invalid or unprivileged.

Dependencies and integration: Exercises strace string quoting, payload truncation, pointer fallback, keyring xlat decoding, and syscall result formatting.

Risks: Large Cartesian output must stay aligned with test expectations; changing string abbreviation limits or keyring xlat names affects many lines.

Test signals: Expected output covers NULLs, bad pointers, escaped binary strings, truncated payload/description, unknown numeric keyrings, and `KEY_SPEC_THREAD_KEYRING`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/add_key.c -->
