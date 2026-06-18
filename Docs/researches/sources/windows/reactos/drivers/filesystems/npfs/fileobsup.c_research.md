# File Research: sources/windows/reactos/drivers/filesystems/npfs/fileobsup.c

## Purpose
Provides NPFS file-object encoding and decoding helpers. These functions map Windows `FILE_OBJECT` fields to NPFS VCB/DCB/CCB contexts and named-pipe end identity.

## Main Responsibilities
- `NpDecodeFileObject`:
  - Reads `FileObject->FsContext`.
  - Decodes the low bit as named-pipe end when present.
  - Returns node type for VCB, root DCB, or CCB.
  - Returns primary context and CCB/root CCB as requested.
- `NpSetFileObject`:
  - Stores primary context in `FsContext`.
  - Stores secondary CCB context in `FsContext2`.
  - Marks pipe file objects with `FO_NAMED_PIPE`.
  - Encodes server end by setting the low bit on a CCB pointer.
  - Sets `PrivateCacheMap` to `(PVOID)1`.

## Important Interactions
- Used by nearly every dispatch path to recover NPFS state from `FILE_OBJECT`.
- Server/client end encoding is consumed by read/write/fsctl/state transitions.
- Root DCB handles store the root DCB in `FsContext` and root CCB in `FsContext2`.

## Risks / Review Notes
- Pointer low-bit tagging assumes all CCB pointers are at least 2-byte aligned, which is true for pool allocations but is a critical invariant.
- `NpDecodeFileObject` writes `*Ccb` unconditionally in recognized cases; callers must pass a valid CCB output pointer.
