# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.cpp

`ApfsContainer` owns APFS container initialization and physical block access. It reads the NX superblock, verifies checksums, scans the checkpoint descriptor ring for the newest or requested XID, enforces Fusion tier2 presence when needed, initializes the checkpoint map and container object map, loads spaceman, optional free-queue trees, and key manager state.

`GetVolume()` maps an APFS filesystem OID through the container OMAP, constructs an `ApfsVolume`, and either initializes the live volume or mounts a requested snapshot. `GetVolumeInfo()` reads a volume superblock without constructing a full volume.

`ReadBlocks()` maps APFS physical addresses to the main or tier2 `Device` based on `FUSION_TIER2_DEVICE_BYTE_ADDR`; `ReadAndVerifyHeaderBlock()` adds checksum verification. Encryption entry points delegate to `KeyManager`.

`dump()` is a high-level diagnostic traversal for container blocks: NXSB, keybag, checkpoint descriptor/data areas, EFI jumpstart, OMAP, spaceman, IP bitmaps, free-queue trees, CABs, and CIBs.

Global debug state is defined here: `int g_debug = 0; bool g_lax = false;`. Notable risks include limited use of `m_main_part_len`/`m_tier2_part_len` bounds and reliance on raw pointer lifetime for supplied devices.
