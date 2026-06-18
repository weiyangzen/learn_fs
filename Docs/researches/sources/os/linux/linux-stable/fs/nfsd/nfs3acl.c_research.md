# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3acl.c

## Summary
Implements NFSACL protocol version 3 server procedures.

## Main APIs
Defines `NULL`, `GETACL`, and `SETACL` procedures and exports `nfsd_acl_version3`.

## Behavior
`GETACL` decodes an NFSv3 filehandle and ACL mask, fetches requested access/default POSIX ACLs, and synthesizes a minimum access ACL when absent. Replies include post-op attributes. `SETACL` validates setattr permission, obtains write access, locks the inode, sets access and default ACLs, and returns post-op attributes.

## Risks
ACL data allocated during decode is released by the procedure path. `GETACL` for default ACLs on non-directories is left to underlying ACL behavior, matching the older comment that Solaris behavior was uncertain.
