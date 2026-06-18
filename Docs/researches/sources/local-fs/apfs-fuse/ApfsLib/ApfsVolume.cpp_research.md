# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.cpp

`ApfsVolume` represents a mounted APFS volume. `Init()` reads and verifies the APFS superblock, initializes the volume OMAP, handles encrypted volumes by obtaining a VEK through `ApfsContainer`, and initializes root, extent-ref, snapshot metadata, and sealed-volume fext trees.

`MountSnapshot()` starts from a live volume superblock, looks up snapshot metadata by XID, reads the snapshot superblock, repeats encryption setup, and initializes volume trees for the snapshot view.

`dump()` renders the volume superblock, volume OMAP, OMAP snapshot tree, ER state, OMAP tree, filesystem tree, snapshot metadata tree, optional integrity metadata, snapshot metadata extension, and fext tree.

`ReadBlocks()` delegates to container physical reads, then decrypts AES-XTS in 0x200-byte units when the volume is encrypted and an XTS tweak is supplied.

`CompareSnapMetaKey()` compares snapshot metadata and snapshot-name keys for snapshot lookup.

Notable risks: encrypted snapshot mounting does not check `container.IsUnencrypted()` the same way `Init()` does. Sealed-volume fext tree support is present, but some crypto handling is marked TODO elsewhere.
