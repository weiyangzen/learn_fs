# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_init.c

ACL allocation and duplication. `acl_init()` rejects negative counts and counts above `ACL_MAX_ENTRIES`, allocates aligned `struct acl_t_struct` storage with `posix_memalign()`, zeroes it, sets the brand to unknown, and sets kernel ACL max count.

`acl_dup()` allocates a fresh ACL, copies the structure, and resets both source and destination iteration cursors.
