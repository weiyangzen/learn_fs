<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_instruction_pointer.c -->
# sources/test-tools/strace/src/print_instruction_pointer.c

Purpose: prints the current tracee instruction pointer as a fixed-width output attribute.

Important APIs/types/functions: `print_instruction_pointer` and `get_instruction_pointer`.

Control flow: begins an attribute, fetches IP, prints 8 hex digits for 32-bit personalities or 16 for 64-bit, prints question marks if unavailable, then emits trailing space.

State and persistence behavior: no state.

Dependencies and integration points: used by syscall output prefixes when instruction pointer display is enabled; depends on current word size and architecture ptrace support.

Risks: unavailable IP must remain visually distinct and width-stable. Current word size controls formatting, not host pointer size.

Test signals: 32-bit and 64-bit tracees, failed IP fetch, and output prefix formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_instruction_pointer.c -->
