# sources/sync-backup/bup/lib/bup/gc.py

## Purpose
`gc.py` implements bup's mark-and-sweep garbage collector. It identifies live objects reachable from refs, rewrites/deletes packs with garbage, and refreshes derived lookup structures.

## APIs and Control Flow
`count_objects` sums object counts across idx files. `report_missing` logs missing objects for ignore-missing mode. `find_live_objects` creates a temporary Bloom filter for live blobs plus a set of live non-blobs, walks refs with `walk_object`, optionally uses broad `PackIdxList` existence checks, and returns liveness structures. `sweep` opens a `LocalRepo` writer with duplicate allowance and an `on_pack_finish` callback, scans each idx, decides whether packs are fully dead, sufficiently live, or require rewrite, writes live objects to new packs, queues stale pack stems, and deletes stale pack-related files after safe points. `bup_gc` counts objects, marks live data, clears midxes/bloom/reflog, calls `sweep`, and warns if interrupted.

## State, Dependencies, Integration, Risks, Tests
Persistent effects include deleting pack files, writing new packs, clearing `bup.bloom`, removing `.midx`, and expiring Git reflogs. Dependencies include `bloom.BloomWriter`, `git.walk_object`, `git.catpipe`, `midx.clear_midxes`, `bloom.clear_bloom`, `LocalRepo`, and external `git reflog expire`. Risks are probabilistic blob retention, interruption after clearing derived data, missing object handling, stale pack deletion timing, reliance on pack stem regex, remote/client index cache interactions, and memory use for live trees. Test signals include zero-object no-op, missing object failure vs ignore logging, live object marking, threshold rewrite decisions, pack deletion after callback, abort on exceptions, reflog command failure, and derived index cleanup.
