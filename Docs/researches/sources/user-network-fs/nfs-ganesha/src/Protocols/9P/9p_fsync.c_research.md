## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_fsync.c

Purpose: implements 9P `TFSYNC` by committing cached file data through FSAL.

APIs and flow: `_9p_fsync` decodes tag/fid, validates the fid, initializes op context, calls `fsal_commit(pfid->pentry, 0, 0)` to commit the whole file, maps FSAL errors through `_9p_tools_errno`, and returns `RFSYNC`.

State/dependencies: it does not mutate fid structure except through any FSAL-side persistence. It depends on valid fid object handles and FSAL commit semantics where count zero means whole file.

Risks/tests: test unopened vs open regular files, directory/object fsync behavior according to FSAL, FSAL retry/error mapping, and invalid fid handling.
