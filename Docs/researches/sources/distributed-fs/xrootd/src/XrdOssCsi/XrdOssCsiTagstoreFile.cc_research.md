# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.cc

## Purpose
Implements the file-backed CSI tagstore. The on-disk format is a 20-byte header followed by one 32-bit CRC tag per data page.

## Important APIs and control flow
`Open()` opens the sidecar through the wrapped `XrdOssDF`, determines machine endianness, attempts to read and validate the header magic and header CRC, initializes a new header if needed, warns on tracked-size disagreement, and calls `ResetSizes()`. A local guard closes the descriptor if initialization fails. `ResetSizes()` compares expected sidecar length with `Fstat()` and either truncates an overlong tag file or reduces the tracked size if the sidecar is short. `Fsync()`, `Flush()`, and `Close()` forward to the underlying descriptor.

`WriteTags()` and `ReadTags()` translate tag offsets to byte offsets at `20 + 4 * off`, using swapped variants when file and machine endian differ. `Truncate()` first adjusts sidecar length, then updates the header tracked size and, when truncating data to zero, marks the tags verified. `WriteTags_swap()` and `ReadTags_swap()` batch 1024 tags through a local conversion buffer.

## State, dependencies, and integration
Persistent state is the header magic, tracked length, flags, header CRC, and tag array. Runtime state includes `trackinglen_`, `actualsize_`, `fileIsBige_`, `machineIsBige_`, `hflags_`, and `isOpen`. It integrates with CSI page code through `XrdOssCsiTagstore`.

## Risks and test signals
Key risks are partial sidecar writes, stale verified flags after data modification, short sidecar recovery reducing coverage, and endian conversion. Tests should open legacy/empty/corrupt headers, round-trip tags on simulated opposite endian data, truncate up/down, and inject short reads/writes from a fake `XrdOssDF`.
