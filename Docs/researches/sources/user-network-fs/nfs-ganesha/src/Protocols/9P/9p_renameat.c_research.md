## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_renameat.c

Purpose: implements directory/name based `TRENAMEAT`.

APIs and flow: `_9p_renameat` validates old and new directory fids, initializes context from the old directory, enforces same-export and write-access checks, copies old/new names, calls `fsal_rename(old_dir, oldname, new_dir, newname)`, and replies `RRENAMEAT`.

State/dependencies: namespace mutation through FSAL without fid mutation. It depends on valid directory fids and export ids.

Risks/tests: test source/destination in same directory and different directories, cross-export failure, long old/new names, overwrite cases, read-only exports, invalid fids, and directory rename constraints.
