# sources/test-tools/strace/src/sigaltstack.c

Purpose: MPERS-aware decoder for alternate signal stack structures.

Important APIs/types/functions: `print_stack_t`, `SYS_FUNC(sigaltstack)`, `stack_t`, `sigaltstack_flags`, `DEF_MPERS_TYPE`, and `MPERS_DEFS`.

Control flow: entry decodes the new `ss` stack pointer/flags/size from tracee memory; exit decodes the old stack pointer if provided.

State and persistence behavior: stateless stack-local fetches; no saved entry data.

Dependencies and integration points: uses personality-aware `stack_t` layout and signal-stack xlat flags. Connected to syscall table entries for `sigaltstack`.

Risks: `stack_t` pointer and size widths vary by personality; MPERS generation must match target ABI. Null or unreadable pointers should stay address-only.

Test signals: null `ss`/`old_ss`, invalid pointers, `SS_DISABLE`/`SS_ONSTACK`, 32-bit personality layout, and successful old-stack output.
