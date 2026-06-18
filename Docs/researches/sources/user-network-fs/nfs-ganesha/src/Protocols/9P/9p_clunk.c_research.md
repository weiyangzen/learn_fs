## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_clunk.c

Purpose: implements `_9p_clunk`, releasing a fid and any associated open state or pending xattr write.

APIs and flow: the handler parses tag/fid, validates the fid table entry, initializes op context from the fid, calls `_9p_tools_clunk`, clears the connection fid slot, and replies with `RCLUNK` or `RERROR`.

State/dependencies: `_9p_tools_clunk` owns most persistence effects: closing open regular files, releasing active parent refs, committing deferred xattr content, releasing group/export/credential/object refs, and freeing the fid. Dependencies are `_9p_proto_tools`, FSAL close/xattr APIs, and op context.

Risks/tests: clunk is the finalizer for many 9P resources, so regressions leak fids or lose deferred xattrs. Test invalid fid, open file close, xattr size mismatch, xattr set failure, and repeated clunk/connection cleanup interactions.
