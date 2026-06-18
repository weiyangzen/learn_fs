## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_setattr.c

Purpose: implements 9P attribute updates.

APIs and flow: `_9p_setattr` parses valid mask and attribute payload, validates fid/write access, optionally gets current time for non-explicit time updates, populates `fsal_attrlist` for mode/owner/group/size/atime/mtime/ctime, calls `fsal_setattr(pfid->pentry, false, pfid->state, &fsalattr)`, releases attrs, and replies `RSETATTR`.

State/dependencies: mutates object metadata through FSAL and may use fid open state. Depends on write export permission and FSAL attr masks.

Risks/tests: test all mask combinations, explicit vs server-current timestamps, truncation through size, owner/group permission/squash behavior, read-only exports, invalid fid, and unsupported ctime updates by FSAL.
