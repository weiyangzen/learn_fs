## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_proto_tools.c

Purpose: shared 9P support routines for credentials, op context setup, FSAL error/open-flag translation, fid finalization, and connection cleanup.

APIs and flow: `_9p_init_opctx` installs fid export and credentials into `op_ctx`; `_9p_release_opctx` releases them. `_9p_tools_get_req_context_by_uid` and `_9p_tools_get_req_context_by_name` map users through `uid2grp`/`uname2grp`. `_9p_tools_errno` maps FSAL status to errno. `_9p_openflags2FSAL` and `_9p_tools_clunk` handle flag translation and fid close/free behavior. `_9p_cleanup_fids` walks all connection fids during teardown.

State/dependencies: owns `_9p_user_cred` refcounts, fid embedded state cleanup, xattr finalization, group-data refs, export refs, object refs, and active open parent refs. Dependencies include idmapper, uid2grp, export manager, FSAL convert, and common memory helpers.

Risks/tests: this file is the resource-lifetime hub. Test fid cleanup under partial attach, xattr write commit/mismatch, multiple opens, credential refcounts, export switching assertions, and connection teardown with many fids.
