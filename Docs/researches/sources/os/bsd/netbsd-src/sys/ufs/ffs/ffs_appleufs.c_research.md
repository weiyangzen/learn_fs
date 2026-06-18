# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_appleufs.c

This file implements Apple UFS label checksum, validation, and creation helpers. It is usable in kernel, standalone, and userland-style builds with fallback includes and assertions.

Key responsibilities:
- Compute Apple UFS label checksums.
- Validate and byte-swap on-disk Apple UFS labels.
- Create a new Apple UFS label with name, timestamp, UUID, and checksum.

Important functions:
- `ffs_appleufs_cksum`: Computes a 16-bit one's-complement checksum over the fixed-size Apple UFS label, matching `in_cksum` style logic.
- `ffs_appleufs_validate`: Checks big-endian magic, copies the label, zeroes and recomputes checksum, byte-swaps fields to host order, validates checksum and name length, clamps long names, NUL-terminates the name, optionally prints DEBUG info, and byte-swaps UUID.
- `ffs_appleufs_set`: Initializes a label. Defaults missing name to `"untitled"`, chooses current time or zero depending on build environment, generates a random UUID in kernel non-standalone builds if none is supplied, clamps/copies name, stores big-endian fields, and computes checksum.

Important interactions:
- Relies on Apple UFS label constants and structure definitions from FFS headers.
- Can be compiled outside kernel with libc includes.

Notable behavior:
- `ffs_appleufs_validate` computes checksum before byte-swapping the magic/version/time/name length fields.
- Name length zero is invalid; overly long names are accepted but clamped.
