# File Research: sources/windows/winbtrfs/src/xor-gas.S

## Purpose

`xor-gas.S` provides GNU assembler implementations of accelerated in-place XOR routines used by WinBtrfs, especially RAID5/RAID6 parity generation.

## Exported Functions

For x86-64:

- `do_xor_sse2`
- `do_xor_avx2`

For 32-bit x86:

- `_do_xor_sse2@12`
- `_do_xor_avx2@12`

Both implement:

```c
void do_xor_*(uint8_t* buf1, uint8_t* buf2, uint32_t len);
```

The operation is:

```c
buf1[i] ^= buf2[i]
```

## Implementation Details

- Uses Intel syntax under GAS via `.intel_syntax noprefix`.
- x86-64 follows the Windows x64 calling convention:
  - `rcx = buf1`
  - `rdx = buf2`
  - `r8d = len`
- 32-bit x86 uses stdcall stack arguments and returns with `ret 12`.
- SSE2 path checks 16-byte alignment on both buffers and uses `movdqa` plus `pxor` for 16-byte blocks.
- AVX2 path checks 32-byte alignment and uses `vmovdqa` plus `vpxor` for 32-byte blocks.
- If alignment is unsuitable or fewer vector-sized bytes remain, the code falls back to word-sized chunks, then byte stragglers.
- x86-64 scalar fallback processes 8-byte chunks; 32-bit fallback processes 4-byte chunks.

## Relationship to Other Files

`write.c` calls the generic `do_xor()` helper for RAID5/RAID6 parity. This assembly file supplies optimized backend routines likely selected by CPU feature detection elsewhere in the driver.

## Research Notes

The file is performance-focused and has no allocation or external state. Correctness depends on callers passing valid writable `buf1`, readable `buf2`, and `len` bytes. The routines intentionally avoid unaligned vector loads by falling back to scalar processing unless both buffers meet the vector alignment requirement.
