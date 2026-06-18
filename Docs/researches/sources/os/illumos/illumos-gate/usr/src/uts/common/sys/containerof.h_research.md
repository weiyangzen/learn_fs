# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/containerof.h

This header defines the private illumos `__containerof(member_ptr, struct_type, member_name)` macro. With GCC 3.1+ it uses statement expressions and `__typeof` assignment for extra type checking; otherwise it falls back to offset arithmetic.

It depends on `sys/stddef.h` for `offsetof` and returns the containing structure pointer by subtracting the member offset from the member address.
