# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_valid.c

Implements ACL validation entry points. `acl_valid()` validates POSIX ACL structure in userland by sorting and calling `_posix1e_acl_check()`. `acl_valid_file_np()`, `acl_valid_link_np()`, and `acl_valid_fd_np()` call kernel ACL check syscalls for a path, link, or fd after normalizing legacy ACL type constants.

For POSIX ACL types (`ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`), the file/link/fd variants sort before checking. The fd variant resets `ats_cur_entry` before the syscall. Invalid null arguments return `EINVAL`.

This file bridges pure userland POSIX structural validation and target-aware kernel validation, so it is important for callers that need filesystem-specific ACL acceptability.
