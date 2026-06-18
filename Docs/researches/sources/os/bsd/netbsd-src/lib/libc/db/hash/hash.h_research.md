# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash.h

Defines the private hash table structures, constants, and address macros. `ACTION` enumerates internal operations. `BUFHEAD` describes LRU buffer nodes with optional overflow-page links and flags for modified, disk-backed, bucket, and pinned status. `HASHHDR` is the disk-resident header containing sizing, masks, split/overflow accounting, fill factor, key count, bitmap locations, and hash signature. `HTAB` is the memory-resident hash handle.

The header defines default sizing parameters, overflow-address encoding (`SPLITSHIFT`, `SPLITMASK`, `OADDR_OF`), bucket-to-page and overflow-address-to-page translations, and pointer-tagging macros used in the bucket directory. It also documents the hash page format for ordinary records, overflow-page pointers, partial keys, full keys, and full key/data continuations.

Dependencies: paired with `page.h` and `extern.h` in every hash implementation file.

Risks/invariants: pointer tagging assumes low address bits are available. `HASH_BSIZE` caps `MAX_BSIZE` to fit uint16_t page offsets without changing the file format. Overflow address space is limited by split/offset bit partitioning.
