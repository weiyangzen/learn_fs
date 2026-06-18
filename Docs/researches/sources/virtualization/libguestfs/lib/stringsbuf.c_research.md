# File Research: sources/virtualization/libguestfs/lib/stringsbuf.c

Expandable NULL-terminated string vector utility.

Important behavior:
- `guestfs_int_add_string_nodup` appends an owned string pointer and grows capacity in chunks of 64.
- `guestfs_int_add_string` appends a duplicated string.
- `guestfs_int_add_sprintf` formats a string with `vasprintf` and appends it.
- `guestfs_int_end_stringsbuf` appends the terminating NULL.
- `guestfs_int_free_stringsbuf` frees all stored strings and the vector.
- Separate from the daemon-side stringsbuf type.

Filesystem relevance:
- Shared utility for APIs that return string lists, including libvirt auth credential lists and storage-related result vectors.
