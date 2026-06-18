# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.c

## Purpose

This file implements AVL indexes for MDCACHE directory entries. It supports lookup by name, lookup by FSAL cookie for chunked readdir, sorted-order indexing, deletion marking, chunk detachment, duplicate handling, and cleanup of a directory's cached dirents. The source was read as a complete 609-line file.

## Important APIs, Types, and Functions

Public functions are `mdcache_avl_init`, `avl_dirent_set_deleted`, `unchunk_dirent`, `mdcache_avl_remove`, `mdcache_avl_insert_ck`, `mdcache_avl_insert`, `mdcache_avl_lookup_ck`, `mdcache_avl_lookup`, and `mdcache_avl_clean_trees`. It uses `mdcache_entry_t`, `mdcache_dir_entry_t`, `struct dir_chunk`, AVL nodes `node_name`, `node_ck`, `node_sorted`, CityHash or Murmur3 name hashes, and MDCACHE LRU chunk/entry references.

## Control Flow

Initialization creates three AVL trees per directory. Insert computes a name hash, inserts into the name tree, optionally inserts into the cookie tree for chunked dirents, and handles duplicate names by comparing cache keys, replacing stale entries, or returning duplicate/cookie-collision errors. Delete marking removes active names, marks dirents deleted, deletes their key, and adjusts `first_ck` across chunks. Removal frees entry refs, unchunks when needed, removes detached dirents, deletes keys, and frees memory.

## State and Persistence Behavior

All state is in memory under the parent directory's `fsobj.fsdir.avl` trees and chunk lists. Cookie and name indexes persist only while the cache entry/chunk remains alive. Dirent deletion may keep chunked entries in the cookie tree so readdir can restart at old positions and skip deleted entries.

## Dependencies and Integration Points

This file integrates with `mdcache_int.h`, `mdcache_lru.h`, `mdcache_avl.h`, hash libraries, dirent chunk logic, and readdir helpers. Callers are expected to hold the parent `content_lock` for write on mutation.

## Risks and Edge Cases

Duplicate file names with different cookies and FSAL cookie collisions make READDIR unreliable and return negative codes. Chunk lifetime is subtle because `mdcache_avl_lookup_ck` returns a dirent while taking a chunk ref. Deleted chunk entries remaining in cookie lookup require all enumeration paths to skip deletion flags.

## Test Signals

Test insert/lookup/remove by name, chunked cookie lookup and unref, duplicate names with same/different keys, duplicate cookies, deletion of first chunk entry updating `first_ck`, full tree cleanup, and debug builds that assert `content_lock` ownership.
