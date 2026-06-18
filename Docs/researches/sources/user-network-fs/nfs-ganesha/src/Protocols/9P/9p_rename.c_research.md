## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rename.c

Purpose: implements fid-based rename.

APIs and flow: `_9p_rename` validates source fid and destination directory fid, initializes context from the source, checks write access and same-export constraints, copies the new name, calls `fsal_rename(pfid->ppentry, pfid->name, pdfid->pentry, newname)`, and returns `RRENAME`.

State/dependencies: changes namespace while keeping fid object handles unchanged. Depends on valid parent/name metadata from earlier walk and FSAL rename semantics.

Risks/tests: test cross-export `EXDEV`, stale `pfid->name`, renaming open files, overwrite behavior, long names, read-only exports, and cache consistency after rename.
