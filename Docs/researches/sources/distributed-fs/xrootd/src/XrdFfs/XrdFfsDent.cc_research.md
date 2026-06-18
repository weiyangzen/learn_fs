# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.cc

## Purpose

This file implements directory-entry list utilities and a small global directory-entry cache for XrdFfs. It supports merging directory listings from many data servers, sorting and de-duplicating names, and remembering recent listings so later stat calls can avoid expensive fan-out.

## Important APIs, Types, and Functions

List helpers are `XrdFfsDent_names_add()`, `XrdFfsDent_names_join()`, `XrdFfsDent_names_extract()`, and `XrdFfsDent_names_del()`. They manipulate `XrdFfsDentnames` linked lists and convert them to sorted `char**` arrays with `qsort()`.

Cache helpers are `XrdFfsDent_cache_init()`, `XrdFfsDent_cache_fill()`, `XrdFfsDent_cache_search()`, and `XrdFfsDent_cache_destroy()`. Internal `XrdFfsDentcache` records hold a directory name, sorted entry array, creation time, lifetime, and entry count. There are 20 global cache slots protected by `XrdFfsDentCaches_mutex`.

## Control Flow

Directory fan-out code collects names in per-server lists, joins those lists, then calls `names_extract()` to sort and destroy the linked-list nodes while transferring name ownership to the returned array. `cache_fill()` updates an existing matching slot if present; otherwise it replaces an expired or invalid slot. `cache_search()` checks each slot for either an exact directory path match or a member name inside a cached directory.

## State and Persistence Behavior

All state is process-local. Cache entries duplicate directory and entry strings and expire after `nents / 10` seconds for replacement purposes, while `dentcache_invalid()` treats entries as unusable after about eight hours because redirector memory may expire.

## Dependencies and Integration Points

The cache is used by `XrdFfsPosix_readdirall()` after merged listings and by `XrdFfsPosix_statall()` as a fast path for files known from a directory listing. It exports a C ABI for the FUSE-oriented code.

## Risks and Edge Cases

The path assembly in `dentcache_search()` uses a fixed 1024-byte buffer with `strcpy()`/`strcat()`, so long paths can overflow. Cache lifetime is proportional to entry count, making tiny directories expire immediately. `names_extract()` transfers name pointers to the caller and destroys nodes, so ownership mistakes can double-free or leak names.

## Test Signals

Tests should cover list add/join/extract ordering, duplicate filtering by callers, cache replacement, exact directory hits, member hits, invalidation after time changes, empty directories, long paths, and concurrent cache search/fill.
