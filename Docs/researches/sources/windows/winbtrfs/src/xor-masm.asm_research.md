# File Research: sources/windows/winbtrfs/src/xor-masm.asm

## Purpose

`xor-masm.asm` is the MASM equivalent of `xor-gas.S`. It provides the same accelerated in-place XOR routines for Microsoft assembler builds.

## Exported Functions

For x86-64 MASM builds:

- `do_xor_sse2`
- `do_xor_avx2`

For 32-bit x86 MASM builds:

- `do_xor_sse2@12`
- `do_xor_avx2@12`

Both implement:

```c
void do_xor_*(uint8_t* buf1, uint8_t* buf2, uint32_t len);
```

## Implementation Details

- Uses `IFDEF RAX` to distinguish 64-bit and 32-bit assembly.
- Enables `.686P` and `.xmm` for 32-bit builds.
- Defines routines inside `_TEXT SEGMENT`.
- x86-64 uses Windows x64 register arguments: `rcx`, `rdx`, `r8d`.
- 32-bit uses stack arguments, saves/restores `esi` and `edi`, and returns with `ret 12`.
- SSE2 routine uses 16-byte aligned `movdqa` and `pxor`.
- AVX2 routine uses 32-byte aligned `vmovdqa` and `vpxor`.
- Scalar fallback handles 8-byte chunks on x86-64 and 4-byte chunks on x86, then byte tails.

## Relationship to Other Files

This is an alternate assembler-source format for the same XOR acceleration used by RAID parity logic in `write.c`. It exists for build environments that use MASM rather than GAS.

## Research Notes

The MASM and GAS versions are functionally parallel. Any future change to one should be mirrored in the other to avoid compiler/toolchain-specific behavior drift.
