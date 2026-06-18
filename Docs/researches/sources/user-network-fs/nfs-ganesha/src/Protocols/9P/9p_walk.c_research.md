## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_walk.c

Purpose: implements fid cloning and path walking.

APIs and flow: `_9p_walk` validates source/new fids, initializes context, allocates a new fid, either clones the source fid for zero components or iteratively `fsal_lookup`s path components, tracks parent/name for later rename/remove, sets qid type/path, allocates embedded 9P state, stores the new fid in the connection table, increments group/user/export/object/parent refs, and returns qids.

State/dependencies: creates persistent fid state and FSAL object references. Depends on `uid2grp`, FSAL lookup, export refs, and `alloc_state`.

Risks/tests: multi-component replies currently return the final qid for every component. Clone path copies the full fid before allocating new state, so refcount and pointer ownership require careful testing. Cover partial lookup failure cleanup, newfid collision, long names, multi-component qids, and clunk ordering.
