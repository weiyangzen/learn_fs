# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_id_to_name.c

Internal id-to-name helper for ACL text output. `_posix1e_acl_id_to_name()` maps `ACL_USER` ids through `getpwuid()` and `ACL_GROUP` ids through `getgrgid()`, unless `ACL_TEXT_NUMERIC_IDS` requests numeric output.

Missing names fall back to decimal ids. The source comments note that the function is not thread-safe because it relies on stateful password/group database APIs.
