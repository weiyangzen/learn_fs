# File Research: sources/os/bsd/netbsd-src/sys/sys/dvdio.h

Defines DVD-ROM specific ioctl ABI and DVD authentication/structure data layouts.

Key content:
- Ioctls: `DVD_READ_STRUCT`, `DVD_WRITE_STRUCT`, `DVD_AUTH`.
- SCSI command constants for DVD structure/key operations.
- DVD structure types: physical, copyright, disk key, BCA, manufacture.
- Structures for physical layers, copyright info, disk key, BCA, manufacture info.
- `dvd_struct` union.
- Authentication state constants for AGID, challenge/key exchange, title key, ASF, RPC state.
- Key/challenge typedefs.
- Authentication payload structs and `dvd_authinfo` union.
- `dvd_rpc_state_t`.

Important behavior:
- Uses C bitfields heavily for protocol fields.
- User/kernel ABI for optical media drivers and tools.
