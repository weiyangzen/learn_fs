# sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.c

## Purpose
Reuses x86_64 PRSTATUS register-set decoding for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_prstatus_regset.c`, which defines `arch_decode_prstatus_regset` for non-m32 builds and delegates to i386 when `MPERS_IS_m32`.

## Control Flow and Integration
The inherited decoder rejects zero or unaligned sizes by printing the address, otherwise fetches a bounded prefix of `struct_prstatus_regset` and prints registers in kernel order, including general registers, `orig_rax`, `rip`, segment selectors, flags, stack pointer, and bases.

## State and Persistence
No state. It reads tracee memory for regset data and emits formatted output.

## Dependencies
Depends on x86_64 PRSTATUS type definition and generic regset code. For m32 mpers builds it depends on the i386 implementation.

## Risks
Partial-size logic prints only fields covered by the fetched size. Any layout mismatch between x32 and x86_64 PRSTATUS would skew all following fields.

## Test Signals
Regset decoding tests should cover full, partial, unaligned, and oversized `NT_PRSTATUS` buffers for x32.
