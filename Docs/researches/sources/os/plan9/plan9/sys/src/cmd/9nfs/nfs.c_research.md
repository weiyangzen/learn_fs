# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.c

Purpose: NFS handle/session translation and NFS attribute conversion helpers.

Key behavior: `rpc2xfid` decodes NFS file handles, authenticates AUTH_UNIX credentials, maps client ids to Plan 9 users, locates cached xfiles, and returns per-user xfids. `setuser`, `xfstat`, `xfopen`, `xfwalkcr`, `xpclear`, and `xp2fhandle` manage 9P fid state and NFS handles. `dir2fattr` converts Plan 9 `Dir` to NFS v2 fattr; `convM2sattr` parses NFS setattr payloads.

Integration notes: core bridge between stateless NFS handles and stateful 9P fids. File handles embed `starttime`, session pointer bits, qid path, and qid type, making them process-lifetime scoped.
