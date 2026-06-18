# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xor.S

## Role

This assembly file implements optimized in-place XOR routines for WinBtrfs parity calculations. It provides SSE2 and AVX2 versions for both x86-64 and 32-bit x86 builds.

The C-side contract is:

- `do_xor_sse2(uint8_t* buf1, uint8_t* buf2, uint32_t len)`
- `do_xor_avx2(uint8_t* buf1, uint8_t* buf2, uint32_t len)`

Both compute `buf1[i] ^= buf2[i]` for `len` bytes.

## x86-64 Implementation

Under `__x86_64__`, the file emits `.code64` routines using the Windows x64 calling convention:

- `rcx`: destination/source buffer `buf1`
- `rdx`: source buffer `buf2`
- `r8d`: byte length

`do_xor_sse2()`:

- Checks both pointers for 16-byte alignment.
- If both are aligned, processes 16-byte chunks with `movdqa`, `pxor`, and `movdqa`.
- Falls back to 8-byte scalar XOR chunks.
- Finishes with byte-by-byte XOR.

`do_xor_avx2()`:

- Checks both pointers for 32-byte alignment.
- If aligned, processes 32-byte chunks with `vmovdqa`, `vpxor`, and `vmovdqa`.
- Falls back to 8-byte scalar XOR chunks.
- Finishes with byte-by-byte XOR.

## 32-Bit x86 Implementation

For non-x86-64 builds, the file emits `.code` routines using stdcall-decorated names:

- `_do_xor_sse2@12`
- `_do_xor_avx2@12`

Arguments are read from the stack into:

- `edi`: `buf1`
- `edx`: `buf2`
- `esi`: length

Both routines save and restore `esi` and `edi`, use `ebp` as a frame pointer, and return with `ret 12`.

The SSE2 path uses 16-byte aligned vector chunks, then 4-byte scalar chunks, then byte chunks. The AVX2 path uses 32-byte aligned vector chunks, then 4-byte scalar chunks, then byte chunks.

## Dependencies And Integration Points

The file includes `asm.inc` and exports symbols consumed by the Btrfs XOR/parity layer, especially RAID5/6 write parity generation in `write.c`. Higher-level C code is responsible for selecting an available SIMD implementation and for providing valid buffers and lengths.

## Risk Notes

- The aligned vector paths use aligned loads/stores (`movdqa`/`vmovdqa`) only after checking both pointers. If either pointer is unaligned, the routine drops entirely to scalar chunks rather than using unaligned vector operations.
- The AVX2 routines do not issue `vzeroupper`; if mixed with legacy SSE code on affected processors this can have performance implications, though not a functional issue.
- The routines assume non-overlapping or safely overlapping buffers for in-place XOR semantics; no overlap handling beyond simple forward iteration is provided.
