## sources/security-integrity/attr/libattr/syscalls.c

Purpose: backwards-compatible symbol-versioned syscall wrappers for historical libattr exports.

It implements `libattr_*xattr` wrappers using `syscall(__NR_*)`, then assigns old symbol versions such as `setxattr@ATTR_1.0` using GCC symver attributes or `.symver` assembly. State is ABI/symbol table only. Dependencies are Linux syscall numbers, compiler symbol-version support, optional visibility attributes, and linker versioning. Risks include LTO/compiler quirks, syscall ABI portability, and maintaining old symbols that libc now normally provides. Tests should inspect exported symbol versions and run old binaries if available.
