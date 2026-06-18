# sources/user-network-fs/libfuse/include/fuse_service_priv.h

`fuse_service_priv.h` defines the private socket protocol between a FUSE server and the mount.service helper. It specifies command/reply magic values, protocol versions, flags, packet layouts, variable-length sizing helpers, and internal service argument names.

Important structs include `fuse_service_memfd_arg`, `fuse_service_memfd_argv`, `fuse_service_packet`, hello and hello-reply packets, simple replies, requested-file replies, fsopen/open/string/mountpoint/bye/mount commands, and inline helpers for null termination and variable-length packet sizes. The internal parser hook is `fuse_parse_cmdline_service`. Numeric fields are documented as network byte order across the socket.

Protocol flow starts with helper hello and server version reply. The server then sends open, block-device open, fsopen/source/mount-options/mountpoint/mtab/mount, and goodbye commands; the helper replies with errors or requested-file packets plus file descriptors through the socket layer. State includes negotiated version, helper flags, paths, open flags, create modes, block size, mount flags, mountpoint format, and exit code.

Risks include ABI mismatches, missed endian conversion, accepting oversized packets above `FUSE_SERVICE_MAX_CMD_SIZE`, missing null termination, invalid flag acceptance, and off-by-one variable packet sizes. Test signals include negotiation boundaries, endian conversion, unknown magic rejection, oversized command rejection, null checks, size helpers, allowed flag masks, open/block-device encoding, mount command encoding, goodbye status, and fake-helper round trips.
