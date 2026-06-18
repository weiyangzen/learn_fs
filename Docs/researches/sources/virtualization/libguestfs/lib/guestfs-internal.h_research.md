# File Research: sources/virtualization/libguestfs/lib/guestfs-internal.h

Purpose: Primary private header for the libguestfs library implementation under `lib/`.

Key contents:
- Defines scoped mutex locking via cleanup attributes.
- Defines defaults and platform constants for appliance memory, launch timeout, machine type, virtio device naming, and appliance networking addresses.
- Defines core enums and structs: handle state, event registry entries, drive source/server/drive records, backend ops, connection ops, feature cache, version, and the full `struct guestfs_h`.
- `guestfs_h` centralizes configuration, runtime paths, error TLS, event callbacks, private data, protocol connection, FUSE state, libvirt auth state, feature cache, and `qemu-img -U` probe cache.
- Declares internal APIs across allocation, errors, actions support, regex matching, string buffers, protocol, sockets, events, tempdirs, drives, appliance building, launch, command execution, qemu helpers, GUID validation, wait helpers, version parsing, and UEFI firmware tables.
- Defines common macros such as `error`, `perrorf`, `warning`, `debug`, `NOT_SUPPORTED`, `ITER_DRIVES`, and `close_file_descriptors`.

Dependencies and state:
- Depends on pthreads, XDR, PCRE2, optional libvirt, and `guestfs-utils.h`.
- This header defines the shared state contract used by nearly every file in this group.

Risks:
- `guestfs_h` is broad and tightly coupled; changes to fields can affect launch, FUSE, callbacks, drives, protocol, and bindings.
- Recursive locking simplifies nested public API calls but can hide lock-order issues if new locks are added.
