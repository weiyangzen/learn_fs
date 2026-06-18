# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/mem.h

## Purpose

Low-level memory, type, endian, byte-swap, and unaligned-access helper header for the imported Zstd/FSE/HUF code.

## Main Components

- Static inline control:
  - `MEM_STATIC`
  - `MEM_STATIC_ASSERT`
  - `MEM_check`
- Sanitizer declarations:
  - MemorySanitizer helpers
  - AddressSanitizer poison/unpoison helpers
- Fixed-width types:
  - `BYTE`
  - `U16`, `S16`
  - `U32`, `S32`
  - `U64`, `S64`
- Architecture helpers:
  - `MEM_32bits`
  - `MEM_64bits`
  - `MEM_isLittleEndian`
- Unaligned memory access:
  - `MEM_read16`, `MEM_read32`, `MEM_read64`, `MEM_readST`
  - `MEM_write16`, `MEM_write32`, `MEM_write64`
- Byte swapping:
  - `MEM_swap32`
  - `MEM_swap64`
  - `MEM_swapST`
- Little-endian helpers:
  - `MEM_readLE16`, `MEM_writeLE16`
  - `MEM_readLE24`, `MEM_writeLE24`
  - `MEM_readLE32`, `MEM_writeLE32`
  - `MEM_readLE64`, `MEM_writeLE64`
  - `MEM_readLEST`, `MEM_writeLEST`
- Big-endian helpers:
  - `MEM_readBE32`, `MEM_writeBE32`
  - `MEM_readBE64`, `MEM_writeBE64`
  - `MEM_readBEST`, `MEM_writeBEST`

## Behavior

- Selects unaligned access strategy through `MEM_FORCE_MEMORY_ACCESS`:
  - `0`: portable `memcpy`
  - `1`: packed structs
  - `2`: direct unaligned loads/stores
- Defaults to packed-struct access on GCC/ICC-style compilers, direct access on some ARMv6 cases, and portable `memcpy` otherwise.
- Provides endian-neutral helpers used by bitstream, FSE, HUF, and Zstd frame/sequence code.

## Dependencies

- `<stddef.h>`
- `<string.h>`
- `<stdint.h>` when available
- MSVC byteswap/intrinsic headers when building under MSVC.

## Research Notes

- This file assumes 32-bit or 64-bit `size_t` and exactly 8-bit bytes.
- Unaligned access mode is a portability/performance tradeoff and can affect strict-aliasing/alignment behavior.
- The bitstream layer depends on `MEM_readLEST` and `MEM_writeLEST` matching the platform `size_t` width.
