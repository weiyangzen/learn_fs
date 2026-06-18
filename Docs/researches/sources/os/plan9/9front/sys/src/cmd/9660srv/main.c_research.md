# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/main.c

9P server front end for `9660srv`.

Key functions:
- `main` parses options, initializes buffer cache/backends, optionally posts a pipe fd in `/srv/<name>`, forks into the background, and starts the 9P I/O loop.
- Options disable Plan 9 extensions (`-9`), Joliet (`-J`), Rock Ridge (`-r`), set cache cluster count (`-c`), set default image/device (`-f`), use stdio (`-s`), and enable verbose tracing (`-v`).
- `io` reads 9P messages, decodes `Fcall`, dispatches through `fcalls[]`, catches server errors through the local jump stack, and writes replies.
- Implements request handlers for version, auth, flush, attach, walk, open, create, read, write, clunk, remove, stat, and wstat.
- `rattach` opens/refs the backing image and lets registered backends try to attach; currently only ISO.
- `doclone` and `rwalk` carefully clone/restores fid state for partial walks.
- `rread` dispatches to directory or file read based on qid type.
- Writes, creates, removes, and wstat are rejected for this read-only filesystem.
- Utility functions include `error`, `nexterror`, `ealloc`, `setnames`, `openflags`, `showdir`, `chat`, and `panic`.

Filesystem relevance: direct. It exposes the ISO backend as a Plan 9 9P file server.
