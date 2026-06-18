# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportsrv.c

This file implements exportfs’s 9P request handlers and blocking worker process pool.

Key responsibilities:
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Tclunk`, `Tstat`, `Tcreate`, `Tremove`, and `Twstat`.
- Enforces read-only mode for mutating requests and write/truncate opens.
- Supports `-S` pseudo-mount attach by mounting the supplied server fd under `/mnt/exportfs/N`.
- Clones fids and walks cached `File` nodes.
- Converts local `Dir` data into 9P stat responses with unique qid paths.
- Dispatches blocking `Topen`, `Tread`, and `Twrite` to slave processes.
- Implements worker allocation, rendezvous dispatch, flush interruption, and worker cleanup.
- Handles mountpoint traversal by spawning a nested exportfs with `openmount`.

Important implementation notes:
- Flush requests locate a busy slave by old tag, set `flushtag`, and post a `"flush"` note.
- `blockingslave` replies to pending flush tags after leaving the busy section.
- `slaveread` uses `preaddir` for filtered directories when a pattern file is active.
- `openmount` carefully closes fds before execing `/bin/exportfs -S/fd/N`.
