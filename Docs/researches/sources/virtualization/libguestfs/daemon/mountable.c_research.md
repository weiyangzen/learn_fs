# File Research: sources/virtualization/libguestfs/daemon/mountable.c

Converts internal `mountable_t` values into protocol structs.

Important behavior:
- Allocates `guestfs_int_internal_mountable`.
- Copies type, device string, and volume string.
- Converts null device/volume fields to empty strings.
- Cleans up partial allocations on failure.

Filesystem relevance: diagnostic/introspection bridge for mountable parsing results.
