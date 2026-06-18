# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_lookup.c

Read completely: 1248 lines.

Implements ULFS directory lookup, directory-entry insertion/removal/rewrite, directory emptiness checks, and directory block reads.

Lookup flow:
- `ulfs_lookup()` resolves a pathname component in a locked directory vnode.
- Checks execute permission on the directory and read-only mount constraints for delete/rename.
- Consults the name cache first and returns cached hits/misses.
- Requires an exclusive directory lock for uncached scans.
- Stores lookup side results in `dp->i_crap` and increments `i_crapcounter`, an acknowledged awkward stale-result scheme.
- Optionally uses `ulfsdirhash` for large directories to find entries and insertion slots.
- Otherwise scans directory blocks linearly, optionally starting from cached `ulr_diroff` and doing a second pass from the beginning.
- While scanning, validates enough entry structure for forward progress and, when `lfs_dirchk` is set, performs fuller checks with `ulfs_dirbadentry()`.
- Computes insertion/removal metadata: offsets, previous-entry distances, free slot size, and end offset for possible truncation.

Directory update helpers:
- `ulfs_direnter()` writes a new directory entry using prior lookup results. It can allocate a fresh directory block, split/compact an existing slot, update dirhash state, write the buffer synchronously, update directory timestamps, and truncate trailing unused directory space.
- `ulfs_dirremove()` removes an entry or replaces it with a whiteout, updates dirhash state, merges freed record length into the previous entry when possible, decrements the target inode link count, writes the buffer, and calls `ulfs_snapgone()` if a snapshot loses its last name.
- `ulfs_dirrewrite()` repoints an existing entry to a new inode number/type, decrements the old inode's link count, writes the buffer, marks parent flags, and handles last snapshot reference.
- `ulfs_dirempty()` scans a directory and returns true only if entries are empty/whiteout or valid `.`/`..` references.

Support helpers:
- `ulfs_dirbad()` reports corrupt directory entries and panics on writable mounts.
- `ulfs_dirbadentry()` validates record length alignment, block fit, minimum size, name length, and NUL termination.
- `ulfs_direntry_assign()` fills inode, name length, type, name bytes, and trailing NUL without setting record length.
- `ulfs_blkatoff()` reads the filesystem block containing a directory offset, optionally with read-ahead controlled by `ulfs_dirrablks`.

Whiteouts and cache:
- Whiteout entries are recognized when directory entries use `LFS_DT_WHT`.
- Found whiteouts can be treated as not found with `ISWHITEOUT` set, preserving create/delete behavior.
- Negative cache entries are inserted for non-create misses.

Risks and notes:
- Directory corruption on writable mounts is treated as panic-worthy.
- Several comments note obsolete or questionable 4.2BSD artifacts and asymmetric link-count behavior.
- `ulfs_dirremove()` decrements link count before buffer write and comments that callers do not account for partial failure.
- `ulfs_dirremove()` uses `ip->i_lfs` inside an `#ifdef LFS_DIRHASH` block even though `ip` may be null in the function signature.
- `ulfs_blkatoff()` allocates temporary read-ahead arrays per call.
