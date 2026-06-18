# File Research: sources/virtualization/nbdkit/plugins/guestfs/guestfs-plugin.c

This plugin uses libguestfs to expose a file or block device from inside disk images or libvirt domains over NBD.

Configuration:
- `export` is required and names the device or file inside the guestfs appliance.
- At least one `disk` or `domain` is required.
- `format` applies to subsequent disk arguments.
- `connect` sets libvirt URI for domains.
- `mount` can be `inspect`, `DEVICE`, or `DEVICE:MOUNTPOINT`.
- `debug` and `trace` enable libguestfs verbosity/tracing.

Connection setup:
- Creates a libguestfs handle with no environment.
- Parses guestfs environment after explicit handle creation.
- Installs a libguestfs event callback that forwards logs to `nbdkit_debug`.
- Adds disks/domains in original user order using recursion over reverse-built lists.
- Launches guestfs, mounts requested filesystems, then determines exported size with either block-device or file APIs.

I/O behavior:
- Uses serialized-connections thread model.
- `.pread` calls `guestfs_pread_device` or `guestfs_pread` in a loop.
- `.pwrite` calls the matching write API in a loop.
- `.flush` calls `guestfs_sync`.
- Errors are translated through `guestfs_last_error` and `guestfs_last_errno`.

Risks and edge cases:
- `mount` parsing mutates the config string after casting away `const`.
- Recursive list replay could be deep for very many disks/mounts, though typical use is small.
- Read/write loop depends on libguestfs returning progress; zero-size progress would be problematic but is not expected.
- Export path beginning `/dev/` decides block-device mode.
