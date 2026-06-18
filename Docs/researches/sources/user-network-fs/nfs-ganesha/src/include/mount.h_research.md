# sources/user-network-fs/nfs-ganesha/src/include/mount.h

## Purpose

`mount.h` is the rpcgen-style MOUNT protocol declaration for MOUNT v1/v3 support. It defines mount status codes, export and mount list wire structures, procedure numbers, auth flavor constants, and XDR prototypes.

## Important APIs, Types, and Functions

Key types are `mountstat3`, `fhandle3`, `mnt3_dirpath`, `groupnode`, `exportnode`, `mountbody`, `mountres3_ok`, and `mountres3`. Constants include `MOUNTPROG`, `MOUNT_V1`, `MOUNT_V3`, `MOUNTPROC*_MNT/DUMP/UMNT/UMNTALL/EXPORT`, `MNT_V3_NB_COMMAND`, `MNTPATHLEN`, `MNTNAMLEN`, and MOUNT-specific RPCSEC_GSS flavor IDs. XDR functions encode/decode each wire type.

## Control Flow

MOUNT service descriptors use the procedure numbers to decode requests into these types, call handlers declared in `nfs_proto_functions.h`, and encode mount results or export lists. The `mountres3` union only carries `mountinfo` on `MNT3_OK`.

## State and Persistence Behavior

The header defines wire data only. Runtime mount lists and export lists are built by server code and freed by corresponding protocol free functions.

## Dependencies and Integration Points

It depends on `gsh_refstr.h` for reference-counted export path storage. It is included by `nfs23.h` and `nfs_proto_data.h`, and integrates with export manager, MOUNT dispatch tables, and XDR code.

## Risks and Test Signals

The comment that `fhandle3` is overlaid with `nfs_fh3` is a compatibility risk: layout changes can break MOUNT/NFS handle interchange. Tests should XDR round-trip mount responses, verify auth flavor arrays, validate export path/group list freeing, confirm procedure table bounds using `MNT_V3_NB_COMMAND`, and compile C/C++ flexible-array branches.
