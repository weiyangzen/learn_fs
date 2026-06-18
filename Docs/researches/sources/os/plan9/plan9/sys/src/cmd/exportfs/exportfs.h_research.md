# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.h

Shared definitions for `exportfs`.

Key contents:
- Structures:
  - `Fsrpc`: work buffer, active pid, interrupt/flush metadata, incoming `Fcall`, and data buffer.
  - `Fid`: exported fid state, local fd, cached `File`, open mode, mount id, directory read cache, and directory offset state.
  - `File`: cached namespace node with name, refcount, qid, qid-table entry, invalid flag, parent/child links.
  - `Proc`: slave worker process list.
  - `Qidtab`: refcounted mapping from real qids to exported unique qid paths.
- Constants for worker counts, fid hash size, qid hash size, and mount map size.
- Global variables for work queue, root files, fid hash/free list, worker process list, mount map, qid table, message size, service fd, and exclusion pattern file.
- Prototypes for 9P handlers, slave I/O operations, fid/file/qid lifecycle, filters, note handling, exclusions, and directory read filtering.

Filesystem relevance:
- Defines the exported namespace cache, fid table, qid-translation layer, and 9P dispatch interface used by `exportfs`.
