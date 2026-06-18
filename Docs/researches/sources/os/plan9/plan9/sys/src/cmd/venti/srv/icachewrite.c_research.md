# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icachewrite.c

Implements asynchronous writeback of dirty index-cache entries. Random index updates are batched into section workers so writes happen in large sorted disk chunks.

`initicachewrite()` creates per-index-section write/done channels and starts one `icachewriteproc()` per section plus a coordinator. `icachewritecoord()` waits for kicks, snapshots `icachestate()`, starts section writebacks and Bloom writeback, waits for completion, then advances arena tail state with `setatailstate()` on success.

`icachewritesect()` gathers dirty entries for an index-section hash range up to the current arena address, sorts them by score, groups nearby buckets into up to 8 MiB chunks, reads the affected bucket range, inserts or replaces packed `IEntry` records, writes the range back, updates any matching disk-cache blocks, and marks successfully written entries clean.

The scheduler respects `icachesleeptime` and `minicachesleeptime`, calling `disksched()` between chunks. Bucket overflow or bad bucket validation leaves entries dirty and reports errors.
