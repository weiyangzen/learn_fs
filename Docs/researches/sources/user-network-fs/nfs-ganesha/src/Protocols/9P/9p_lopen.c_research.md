## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lopen.c

Purpose: opens an existing fid using 9P2000.L open flags.

APIs and flow: `_9p_lopen` validates fid, translates flags to FSAL open flags and share access, initializes op context, optionally adds truncation, calls `fsal_reopen2` for regular files, increments `pfid->opens`, holds an active parent reference, and returns qid/iounit.

State/dependencies: mutates fid open count and embedded FSAL state. Non-regular objects return success without FSAL open, relying on object type semantics elsewhere.

Risks/tests: open count/ref balancing with repeated opens and clunk is important. Test read/write/truncate modes, regular vs directory/special files, FSAL reopen failure, stats with later read/write, and parent ref release.
