# File Research: sources/os/linux/linux/fs/xfs/scrub/agheader_repair.c

This file implements online repair for the same AG header objects checked by `agheader.c`: secondary superblocks, AGF, AGFL, and AGI. Repair is deliberately conservative and generally requires rmapbt support for reconstructing allocation group state from reverse mappings.

`xrep_superblock` repairs only secondary superblocks. It refuses AG 0, obtains the secondary superblock buffer, zeroes it, copies the mounted primary superblock into it, clears secondary-ignored NEEDSREPAIR and log-incompat feature bits, sets the buffer type, and logs the full block.

The AGF repair flow uses `xrep_find_ag_btree_roots` and rmap ownership to rediscover bnobt, cntbt, rmapbt, and refcountbt roots. It validates candidate roots and checks that the rediscovered rmapbt root matches the old AGF, because the rmapbt is the trusted source used to rebuild the header. `xrep_agf_init_header` rewrites the AGF fixed fields while preserving AGFL ring state, marks perag AGF state stale, installs roots, recalculates free-block, longest-free, btree-block, rmap-block, and refcount-block counters by walking the rebuilt btrees, logs the result, reinitializes perag counters, and rolls the AG transaction.

The AGFL repair path identifies AGFL blocks by collecting OWN_AG rmaps and subtracting current bnobt, cntbt, rmapbt, and cross-linked metadata blocks. It caps the rebuilt AGFL to the AGFL array size, rewrites the AGFL header and block array, updates AGF ring counters, rolls the transaction, and reaps overflow blocks back to free space.

The AGI repair path finds inobt and optional finobt roots through rmap data, rewrites AGI fixed fields, recalculates inode and btree block counters, and rebuilds unlinked inode buckets. The unlinked repair logic combines existing on-disk bucket walking, incore inode radix-tree scanning, opportunistic on-disk inode reloads, bitmaps of unlinked aginos, and staged `xfarray` next/prev pointer maps. It then logs inode unlinked pointer fixes and writes rebuilt bucket heads into the AGI.

Key risks handled here include chicken-and-egg dependencies between corrupt headers and btree discovery, stale perag state, old buffer verifier races after btree height changes, and preserving/reloading unlinked inode state without losing inodes that require inactivation.
