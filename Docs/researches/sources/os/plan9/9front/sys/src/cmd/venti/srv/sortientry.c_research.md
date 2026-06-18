# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/sortientry.c

`sortientry.c` builds a sorted temporary file of all `IEntry` records implied by arena clump directories. It scans every arena, converts non-corrupt `ClumpInfo` rows into packed entries, marks scores in the bloom filter, bucket-sorts by leading score bits, spills bucket chunks to a temporary `Part`, then reloads and `qsort`s each bucket into final sorted order.

The chunk format stores a linked-list head at the end of each bucket buffer. `sortrawientries()` returns the clump count and final sorted base offset for downstream index rebuild logic.

This file is central to rebuilding indexes from arena truth. Risks are mostly operational: bucket memory sizing, temporary partition I/O failures, and ensuring corrupt clumps are skipped from index entries while still marked in bloom.
