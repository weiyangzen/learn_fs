# File Research: sources/os/linux/linux/fs/xfs/scrub/attr_repair.c

This file repairs extended attribute metadata by salvaging valid attributes, replaying them into a temporary file, and atomically exchanging the rebuilt attr fork into the file being repaired. It supports parent pointer filesystems by capturing live directory updates during repair and replaying those changes into the temporary file before commit.

The repair context `struct xrep_xattr` tracks the tempfile exchange state, staged xattr keys in an `xfarray`, names/values in an `xfblob`, parent pointer update arrays and blobs, a directory update hook, scratch parent pointer arguments, and locking for live update capture. `xrep_setup_xattr` enables directory-entry update gating when parent pointers exist and creates a temporary regular file for the rebuild.

Salvage filters reject incomplete, nameless, oversized, invalid-name, invalid-value, and invalid-parent-pointer attributes. Shortform, local leaf, and remote leaf attributes have separate salvage paths. Remote values are recovered by finding suitable buffers, checking attr leaf structure where possible, reading remote values through XFS attr helpers, and ignoring corrupted remote values rather than failing the whole repair. Staged names and values are periodically flushed into the tempfile when memory use exceeds eight pages.

The non-inline scanner walks attr fork extents, probes the buffer cache and disk for possible attr leaf blocks, salvages entries from structurally plausible leaves, and carefully stales single-block buffers that might alias multiblock remote-value buffers. If parent pointer updates occur during a flush, `xrep_xattr_full_reset` clears the tempfile attr fork and restarts salvage without further periodic flushing to regain a consistent base.

Rebuild completion either zaps the repaired file's attr fork if no attributes were salvaged, or finalizes the tempfile by replaying queued parent pointer updates, preparing both attr forks for exchange, and using `xrep_tempexch_contents` to swap mappings. Local/local forks can be copied directly if the rebuilt shortform data fits. After exchange, the old attr fork now attached to the tempfile is reaped and cached ACLs are invalidated.

The top-level `xrep_xattr` requires both rmapbt, for reaping old attr blocks, and exchange-range support, for atomic replacement. Its major hazards are live parent pointer concurrency, buffer aliasing around remote attrs, memory growth from large attr sets, and preserving valid attrs while discarding corrupt entries.
