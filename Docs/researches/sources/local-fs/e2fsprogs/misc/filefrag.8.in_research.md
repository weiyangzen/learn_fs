# File Research: sources/local-fs/e2fsprogs/misc/filefrag.8.in

## Purpose
Manpage source for `filefrag`, a utility that reports file fragmentation.

## Key Elements
Explains that `filefrag` first uses FIEMAP for extent mapping and falls back to FIBMAP if FIEMAP is unsupported. Documents options for forcing FIBMAP, choosing display block size, printing extent format, querying ext4 extent status cache, preloading cache, syncing before mapping, verbose output, version/flag display, xattr mapping, and hexadecimal extent output.

## Dependencies
References Linux FIEMAP and FIBMAP ioctls and ext4-specific extent status cache behavior.

## Behavior/Risks
Warns implicitly through option descriptions that some modes are kernel- and filesystem-specific. `-B` and FIBMAP behavior can require privileges in the implementation.
