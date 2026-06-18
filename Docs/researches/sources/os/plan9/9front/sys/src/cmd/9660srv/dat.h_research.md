# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/dat.h

Shared data definitions for `9660srv`.

Key contents:
- Defines sector size `2048` and maximum name size `256`.
- `Iobuf` and `Ioclust` describe cached sector buffers grouped into clusters, including device, address, busy count, LRU links, and metadata/data cache tag.
- `Xdata` tracks an underlying ISO image/device file, its qid/type/device identity, open fd, and reference count.
- `Xfsub` is the filesystem operation interface used by the 9P request layer.
- `Xfs` represents an attached filesystem instance, including backing device, operation vector, reference count, SUSP/Rock Ridge/Plan 9 flags, root qid, and private parser state.
- `Xfile` represents a fid, with flags, qid, filesystem reference, and per-fid private `Isofile` state.
- Declares common error strings, globals, options disabling Joliet/Plan 9/Rock Ridge, and error stack state.

Filesystem relevance: direct. It defines the in-memory object model for the ISO 9P filesystem server.
