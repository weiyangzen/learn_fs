# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_branding.c

Internal ACL brand tracking for unknown, POSIX.1e, and NFSv4 ACL semantics. It derives an ACL pointer from an entry pointer via alignment masking, reads/sets `ats_brand`, and checks whether an ACL or entry may be branded as a requested semantic.

Branding controls type validation: NFSv4-branded ACLs accept `ACL_TYPE_NFS4`, POSIX-branded ACLs accept access/default types, and unknown ACLs remain permissive. `acl_get_brand_np()` exposes the current brand after validating arguments.
