# File Research: sources/virtualization/libguestfs/lib/libvirt-auth.c

Libvirt authentication bridge for libguestfs events.

Important behavior:
- Maps libvirt credential constants to API strings such as `username`, `authname`, `passphrase`, and prompt variants.
- `guestfs_impl_set_libvirt_supported_credentials` validates and atomically installs supported credential types.
- `guestfs_int_open_libvirt_connection` opens `virConnectOpenAuth` with either custom event-driven auth or a wrapper around libvirt default auth.
- Custom auth stores requested credentials on the handle and fires `GUESTFS_EVENT_LIBVIRT_AUTH`.
- Event-only getters expose requested credential names, prompt, challenge, and default result.
- `guestfs_impl_set_libvirt_requested_credential` stores a NUL-terminated result buffer for libvirt and records the exact byte length.
- Non-libvirt builds return consistent “compiled without libvirt” API errors.

Filesystem relevance:
- Enables libguestfs to access domains and storage pools whose disk metadata or secrets require libvirt authentication.
