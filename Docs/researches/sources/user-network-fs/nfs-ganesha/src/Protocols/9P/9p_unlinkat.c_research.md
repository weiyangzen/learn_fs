## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_unlinkat.c

Purpose: implements name-based unlink relative to a directory fid.

APIs and flow: `_9p_unlinkat` parses directory fid, name, and unused flags, validates fid, initializes context, checks write access, copies the name, calls `fsal_remove(pdfid->pentry, name)`, and returns `RUNLINKAT`.

State/dependencies: namespace mutation through FSAL, no fid cleanup. Flags are currently ignored.

Risks/tests: test file vs directory removal semantics, ignored flags such as remove-directory intent, long names, read-only exports, invalid directory fid, FSAL error mapping, and cache invalidation.
