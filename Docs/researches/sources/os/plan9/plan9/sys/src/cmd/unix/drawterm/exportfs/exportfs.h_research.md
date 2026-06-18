# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.h

Read fully: 148 lines, 2738 bytes. SHA-256 prefix: `85480938cf1a5c94`.

This is the private header for drawterm’s exportfs library.

It defines:
- `Fsrpc`, holding a pending 9P request, buffer, process/flushtag state, and interrupt flag.
- `Fid`, mapping 9P fid numbers to local file descriptors and cached `File` nodes.
- `File`, a cached path tree node with qid and parent/child links.
- `Proc`, tracking blocking slave worker processes.
- `Qidtab`, mapping local qids to unique exported qid paths.
- Limits for worker count, fid hash size, fid chunk allocation, pseudo mount points, and qid hash size.
- Error string aliases, global state declarations, request handler prototypes, utility prototypes, and no-op `notify`/`noted`/`exits` macros for this portability context.

Integration: included with `Extern` defined differently by `exportfs.c` and `exportsrv.c`.

Risk notes: this header controls global ownership conventions across both exportfs implementation files.
