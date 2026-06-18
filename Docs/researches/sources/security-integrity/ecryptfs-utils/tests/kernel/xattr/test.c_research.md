## sources/security-integrity/ecryptfs-utils/tests/kernel/xattr/test.c

Purpose: C xattr correctness test for eCryptfs. It sets three `user.test*` attributes, validates `listxattr` length and ordering, reads each value back, removes all attributes, and verifies the list is empty.

Important APIs and functions: `setxattr`, `listxattr`, `getxattr`, `removexattr`, static `names` and `values`, `main`. Control flow iterates over known names/values, accumulates expected nul-terminated name-list length, checks `listxattr(NULL,0)`, checks the returned buffer sequentially, validates values, removes each xattr, and confirms no remaining attributes.

State and persistence: Mutates file extended attributes only. Dependencies are Linux xattr APIs and deterministic order from eCryptfs/lower filesystem; order sensitivity is a notable assumption because POSIX does not strongly promise ordering. Integration is via `xattr.sh`. Risk: 1024-byte list buffer is fine for this fixed set; failures indicate xattr passthrough, list sizing, value, removal, or ordering issues.
