# sources/test-tools/strace/src/sram_alloc.c

Purpose: Blackfin-only decoder for `sram_alloc`.

Important APIs/types/functions: `SYS_FUNC(sram_alloc)` and `sram_alloc_flags`.

Control flow: compiled only under `BFIN`. Prints size and allocation flags, then marks return value as decoded hexadecimal.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `<bfin_sram.h>` and the Blackfin syscall table.

Risks: architecture-specific code can bit-rot because modern build/test coverage may be sparse. Flag names must match Blackfin SRAM allocation constants.

Test signals: Blackfin build plus known, combined, and unknown SRAM allocation flags.
