## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mknod.c

Purpose: implements special-file creation for `TMKNOD`.

APIs and flow: `_9p_mknod` validates parent fid/write access/name, maps mode bits to FSAL object type, prepares rawdev and mode attributes, calls `fsal_create`, releases attrs and the returned object ref, then returns a qid.

State/dependencies: changes namespace through FSAL. The gid is parsed but ignored. The qid path is initialized from a local `fileid` variable that remains zero rather than the created object's fileid, which is a notable correctness risk.

Risks/tests: test block/char/fifo/socket creation, invalid mode, rawdev fields, ignored gid, qid path correctness, long names, read-only exports, and FSAL support for special files.
