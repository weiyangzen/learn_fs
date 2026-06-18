# File Research: sources/os/bsd/netbsd-src/lib/libintl/libintl_local.h

Private `libintl` header defining GNU `.mo` file structures and host-side runtime structures.

Includes:
- Magic constants, revision helpers, default domain name, mmap size limit.
- Packed on-disk `.mo`, entry, sysdep segment, and sysdep string structures.
- Host-side converted structures for string tables, plural metadata, charset, hash table, and sysdep data.
- `mohandle` and `domainbinding` structures.
- Globals for domain bindings and current domain.
- Internal prototypes for iconv conversion, gettext string hashing, and sysdep tag expansion.
