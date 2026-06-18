# sources/storage-engines/foundationdb/flow/include/flow/ppc-asm.h

## Purpose
PowerPC assembly support macros imported from GCC for register names, ABI-specific function labels/descriptors, CFI directives, and GNU-stack metadata.

## Important APIs, Types, And Functions
Defines register-number macros for GPRs, condition registers, floating-point, Altivec, and VSX registers. `XGLUE`/`GLUE` build labels. ABI macros include `FUNC_NAME`, `JUMP_TARGET`, `FUNC_START`, `HIDDEN_FUNC`, and `FUNC_END`. Optional CFI macros expand when GCC host config enables them.

## Control Flow
Assembly sources include this file so preprocessor conditionals expand correct labels/prologues for ELFv2, older ppc64 descriptor ABIs, AIX descriptor mode, PIC, and default labels.

## State And Persistence Behavior
No runtime state. It affects object-file symbols, unwind metadata, and stack-note sections.

## Dependencies And Integration Points
Used by PowerPC assembly routines, likely optimized checksum/CRC code. Complements `ppc-opcode.h`.

## Risks And Edge Cases
Broad macros like `r0`, `sp`, and `toc` can pollute C/C++ scope. ABI flags must match compiler and assembler target settings.

## Test Signals
PowerPC build/link success, correct symbols and hidden visibility, valid unwind info, no executable-stack warnings, and passing low-level routine tests.
