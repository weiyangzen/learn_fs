# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/entropy_common.c

## Purpose

Common FSE/HUF entropy helpers shared by compression and decompression. It exposes version/error wrappers, decodes FSE normalized count headers, and reads serialized Huffman weight tables.

## Main Components

- Version/error wrappers:
  - `FSE_versionNumber`
  - `FSE_isError`
  - `FSE_getErrorName`
  - `HUF_isError`
  - `HUF_getErrorName`
- FSE normalized count reader:
  - `FSE_readNCount`
- Huffman statistics reader:
  - `HUF_readStats`

## Behavior

`FSE_readNCount`:

- Reads the table log from the first bits of an FSE header.
- Clears missing symbols in `normalizedCounter`.
- Handles compact runs of zero frequencies.
- Decodes positive counts and `-1` low-probability counts.
- Validates that the normalized total resolves to exactly one remaining unit.
- Updates `maxSVPtr` and `tableLogPtr`.

`HUF_readStats`:

- Reads Huffman weights either as raw 4-bit packed values or as an FSE-compressed weight stream.
- Reconstructs the implied final symbol weight.
- Builds `rankStats`.
- Validates total weight shape and rank-1 constraints.

## Dependencies

- `mem.h`
- `error_private.h`
- `fse.h` with `FSE_STATIC_LINKING_ONLY`
- `huf.h` with `HUF_STATIC_LINKING_ONLY`

## Research Notes

- This file is central to validating compressed entropy table headers.
- `FSE_readNCount` has special handling for headers shorter than four bytes by copying into a temporary four-byte buffer.
- Malformed table logs, impossible totals, missing end markers, and oversized symbol ranges return private Zstd/FSE error codes.
