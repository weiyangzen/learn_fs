## sources/security-integrity/attr/libmisc/walk_tree.c

Purpose: recursive tree walker with symlink, one-filesystem, and file-descriptor-pressure handling.

It tracks visited directories by dev/inode to avoid loops, uses `lstat`/`stat` according to flags, calls the user callback for every path and failures, limits open directory handles based on `RLIMIT_NOFILE`, and reopens closed handles with saved `telldir` positions. State is traversal-local `walk_tree_args`, linked directory handles, mutable path buffer, and callback accumulator return values. Dependencies are POSIX directory/stat APIs. Risks include fixed `FILENAME_MAX` path buffer, complex symlink flag interactions, directory mutation during traversal, and callback error aggregation by addition. Tests should cover recursive symlink loops, ENAMETOOLONG, one-filesystem skipping, and low fd limits.
