## sources/security-integrity/attr/include/walk_tree.h

Purpose: recursive filesystem traversal API for attr tools.

It defines traversal mode flags, callback condition flags, and `walk_tree(path, flags, num_handles, callback, arg)`. Runtime behavior is implemented in `libmisc/walk_tree.c`. State is traversal-local. Dependencies are `struct stat` and callbacks. Risks are flag combinations around symlinks and one-filesystem traversal. Tests should cover recursive, logical, physical, top-level symlink, and failure callbacks.
