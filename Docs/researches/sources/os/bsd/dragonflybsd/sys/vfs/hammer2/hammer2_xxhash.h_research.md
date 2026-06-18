# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xxhash.h

HAMMER2 wrapper header for the bundled xxHash implementation.

Key responsibilities:
- Includes HAMMER2’s vendored `xxhash/xxhash.h`.
- Defines the HAMMER2-specific 64-bit xxHash seed `XXH_HAMMER2_SEED`.
- Provides a small guarded include point for HAMMER2 checksum/hash users.

Dependencies:
- Depends on `sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h`, which namespaces exported xxHash symbols with `h2_`.

Notable risks:
- The seed is part of HAMMER2’s hash/checksum behavior; changing it would alter computed values and compatibility expectations.
- Symbol namespace behavior is controlled in the vendored xxHash header, so wrapper users depend on that header retaining `XXH_NAMESPACE h2_`.
