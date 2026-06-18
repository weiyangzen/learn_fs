# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkidP.h

Purpose: private libblkid header defining internal structures, flags, debug controls, and cross-file prototypes.

Important APIs/types/functions: `struct blkid_struct_dev` stores cache linkage, tag list, name, type, priority, device number, timestamp, flags, label, and UUID shortcut. `struct blkid_struct_tag` links tags by device and by tag name. `struct blkid_struct_cache` stores device/tag list heads, probe/cache-file times, flags, and filename. Defines verification/cache flags, probe timing constants, default cache path `/etc/blkid.tab`, error codes, device priority constants, debug masks, `DBG`, `dir_list`, and private prototypes for scanning, llseek, cache read/save, tags, and device allocation.

State and persistence: describes in-memory cache graph and on-disk cache filename; no state itself.

Dependencies and integration: includes public `blkid.h` and private `list.h`. All libblkid implementation files depend on this shared contract.

Risks and test signals: intrusive list ownership is manual and easy to corrupt; private layout changes affect all objects. Test device/tag add/free, cache flush/read, debug builds, and stale cache cleanup.
