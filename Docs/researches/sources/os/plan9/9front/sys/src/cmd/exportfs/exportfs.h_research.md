# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.h

This header defines exportfs’s shared state, data structures, constants, errors, and function prototypes.

Key structures:
- `Fsrpc`: buffered 9P request wrapper with flush tag and decoded `Fcall`.
- `Fid`: active 9P fid, local fd, associated `File`, open mode, mount id, and cached directory-read state.
- `File`: cached filesystem node with name, refcount, qid, parent/child links, and invalidation flag.
- `Proc`: worker/slave process bookkeeping for blocking I/O.
- `Qidtab`: maps local qids to unique exported qid paths.

Key constants:
- Fid hash size, fid allocation chunk, pseudo mount count, qid hash width/table size.

Important implementation notes:
- `Extern` is controlled by including source files to define or declare globals.
- The header declares all 9P request handlers, I/O helpers, fid/file/qid helpers, allocation helpers, exclusion handling, and directory filtering.
