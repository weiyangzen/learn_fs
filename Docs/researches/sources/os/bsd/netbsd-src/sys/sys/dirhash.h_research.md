# File Research: sources/os/bsd/netbsd-src/sys/sys/dirhash.h

Declares an in-memory directory hash table used to accelerate directory entry lookup and free-space tracking.

Key content:
- Hash sizing: 5 bits, 32 buckets.
- `struct dirhash_entry`: hash value, directory offset, name length, entry size, list linkage.
- `struct dirhash`: flags, byte size, refcount, number of files, entry buckets, free-entry list, global tailq linkage.
- Flags: purged, complete, broken on read-in, compactable.
- APIs: initialize, purge, ref/unref, enter/remove entries, record freed space, lookup names/free entries, emptiness check.

Important behavior:
- Includes `sys/queue.h` and `sys/dirent.h`.
- Stores `d_namlen` to avoid costly fid-to-dirent translations.
