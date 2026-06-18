# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/iobuf.c

Clustered sector buffer cache for `9660srv`.

Key behavior:
- Uses `BUFPERCLUST=64`, so each cache cluster covers 128 KiB of ISO sectors.
- Default `NCLUST=64`, configurable through global `nclust`.
- `iobuf_init` allocates all clusters, per-sector `Iobuf` descriptors, and backing data with `sbrk`, then links clusters into an LRU list.
- Reserves roughly one-eighth of clusters for metadata-tagged reads so directory data is less likely to be evicted by large sequential file reads.
- `getbuf` maps a sector number to its cluster, reads the cluster on miss, and returns the per-sector buffer.
- `putbuf` releases a buffer and moves its cluster to the LRU head.
- `purgebuf` invalidates all cached clusters for a closing backing device.
- `xread` performs contiguous cluster reads from the ISO image/device and records how many sectors were actually read.

Filesystem relevance: direct. This is the read cache used for ISO directory and file data.
