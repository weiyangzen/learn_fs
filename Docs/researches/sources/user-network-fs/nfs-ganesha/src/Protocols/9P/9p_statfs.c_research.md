## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_statfs.c

Purpose: implements filesystem statistics for 9P.

APIs and flow: `_9p_statfs` validates fid, initializes op context, gets object attrs, calls `fsal_statfs`, maps dynamic byte/file counts and rawdev major into the 9P `RSTATFS` payload, and returns constant magic/type, block size, and name length values.

State/dependencies: read-only over object/export state. It depends on FSAL attr/statfs APIs and attr release discipline.

Risks/tests: block size is hard-coded to one while byte counts come from FSAL, so client interpretation should be tested. Cover invalid fid, statfs failure, attr failure, large count encoding, and msize bounds.
