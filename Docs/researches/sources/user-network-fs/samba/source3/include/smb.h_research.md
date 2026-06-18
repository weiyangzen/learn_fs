# sources/user-network-fs/samba/source3/include/smb.h

## Purpose
`smb.h` is a central Samba source3 include that gathers SMB/CIFS protocol constants, packet offsets, open/share-mode encodings, oplock definitions, core server data structures, and server-wide feature identifiers. It also includes the ACL, quota, readdir-attribute, VFS, SMB macro, and name-service headers that many source3 server paths expect through the broad `includes.h`/`smb.h` dependency chain.

## Important APIs, Types, and Constants
- Network constants: `NMB_PORT`, `DGRAM_PORT`, `NBT_SMB_PORT`, `TCP_SMB_PORT`, and `SMB_PORTS` define NetBIOS and direct TCP SMB listener ports.
- Protocol/open constants: deny modes (`DENY_*`), DOS open modes (`DOS_OPEN_*`), `OPENX_*` disposition flags, `NTCREATEX_*` masks/private flags, pipe flags, IOCTL constants, and usershare error codes.
- Packet layout macros: `smb_com`, `smb_tid`, `smb_uid`, `smb_vwv*`, transaction/NT transaction field offsets, and `smb_base()` encode byte offsets into SMB1 packets after the NBT header. These are used by low-level request decoders and reply builders.
- Oplock definitions: protocol request macros (`CORE_OPLOCK_REQUEST`, `EXTENDED_OPLOCK_REQUEST`), local aliases (`NO_OPLOCK`, `EXCLUSIVE_OPLOCK`, `BATCH_OPLOCK`, `LEVEL_II_OPLOCK`, `LEASE_OPLOCK`), return wire values, and `struct kernel_oplocks_ops`.
- Shared types: `struct notify_change`, `struct sys_notify_context`, `struct current_user`, `userdom_struct`, `struct interface`, EA structures, `enum remote_arch_types`, `enum usershare_err`, `enum file_close_type`, and `struct smb_extended_info`.

## Control Flow and State
This header does not implement executable control flow, but it controls parsing and dispatch by defining field offsets and bit extractions that request handlers use directly. Its oplock macros normalize CORE and extended oplock request bits into the common internal flag set, while the kernel-oplock operations table defines the callback shape used by platform-specific oplock backends.

State exposed here is mostly embedded in other server objects. `struct current_user` binds a connection, SMB2-compatible VUID, Unix token, and NT security token. `struct sys_notify_context` stores a tevent context and backend-private change-notify data. `struct interface` models discovered network interfaces with address, netmask, broadcast, speed, and capability metadata.

## Persistence Behavior
No direct persistence is implemented. The header defines persistent or wire-compatible data shapes indirectly: SMB packet offsets, SID sizing, EA names stored as xattrs (`user.DOSATTRIB`, `user.DosStream.`, `user.SmbReparse`, etc.), usershare status codes, and the 48-byte `smb_extended_info` structure used in object-id information replies.

## Dependencies and Integration Points
`smb.h` depends on generated NDR security/server-id headers, `libcli/smb/smb_common.h`, role constants, quota and VFS headers, SMB ACLs, name service declarations, and macro helpers. Because it pulls in `vfs.h` and `smb_macros.h`, edits can affect most source3 server modules, especially SMB1 transaction handling, file open paths, ACL/quota code, browser announcements, and xattr stream handling.

## Risks
- Packet offset macros are ABI-sensitive; an incorrect offset silently corrupts SMB1 parsing or response generation.
- The open/disposition and oplock bit masks are protocol boundary constants. Changes can break Windows client compatibility or server-side share-mode/oplock semantics.
- The broad include role can amplify compile breakage or dependency cycles.
- Samba-private xattr names must stay synchronized with code that reads or writes those EAs, as noted for POSIX inheritance.

## Test Signals
Relevant signals include SMB1 open/create/trans/NT-trans torture tests, oplock/lease torture coverage, EA/xattr stream tests, usershare parsing tests, and compile coverage for source3 modules that include `smb.h`. Packet-level tests should catch regressions in `smb_vwv*` and transaction offset macros.
