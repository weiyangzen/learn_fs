## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mkdir.c

Purpose: implements `TMKDIR`.

APIs and flow: `_9p_mkdir` validates parent fid, initializes op context, enforces write access, copies the name, prepares mode attributes, calls `fsal_create` with `DIRECTORY`, releases attrs, drops the returned object reference, builds a directory qid from fileid, and returns `RMKDIR`.

State/dependencies: changes namespace through FSAL but does not allocate a new fid. The gid request field is parsed and logged but not applied.

Risks/tests: test mode application, ignored gid behavior, long names, read-only exports, parent not directory, existing names, and returned qid validity after the object ref is released.
