# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/iobuf.c

Purpose: clustered read cache for ISO image sectors.

Key behavior: `iobuf_init` allocates `nclust` clusters, each with `BUFPERCLUST` sector buffers. `getclust` finds cached clusters or reuses an idle one, reads via `xread`, and tracks busy counts. `putclust` decrements busy count and moves clusters to the LRU head. `getbuf`/`putbuf` expose single-sector buffers; `purgebuf` invalidates device clusters.

Integration notes: tuned for large contiguous ISO reads. `getbuf` errors on short reads beyond cached cluster contents. Multiple mounted images share the global cache.
