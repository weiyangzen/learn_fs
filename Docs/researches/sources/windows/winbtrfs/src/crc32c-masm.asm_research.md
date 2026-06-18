# File Research: sources/windows/winbtrfs/src/crc32c-masm.asm

## Role

`crc32c-masm.asm` provides MASM CRC32C implementations for MSVC x64 and x86 builds.

## x64 Path

- Chosen under `IFDEF RAX`.
- Declares `EXTERN crctable:qword`.
- Exports `calc_crc32c_sw` and `calc_crc32c_hw`.
- Uses Windows x64 calling convention with seed in `rcx`, buffer in `rdx`, and length in `r8`.
- Software path uses the table-driven byte loop.
- Hardware path uses `crc32` over 8-byte chunks, then 4-byte, 2-byte, and 1-byte tails.

## x86 Path

- Uses `.686P` when not assembling x64.
- Declares `EXTERN crctable:ABS`.
- Exports `calc_crc32c_sw@12` and `calc_crc32c_hw@12`.
- Preserves `esi` and `ebx` in the software path.
- Reads arguments from the stack and returns with `ret 12`.
- Hardware path uses `crc32` over 4-byte chunks, then 2-byte and 1-byte tails.

## Dependencies

- Depends on `crctable` from `crc32c.c`.
- Provides the x86/x64 symbols declared in `crc32c.h` when building with MSVC/MASM.

## Research Notes

- This is functionally parallel to `crc32c-gas.S`, with syntax and symbol decoration adapted for MASM.
- Hardware routines require external CPU feature selection before the function pointer is redirected to `calc_crc32c_hw`.
