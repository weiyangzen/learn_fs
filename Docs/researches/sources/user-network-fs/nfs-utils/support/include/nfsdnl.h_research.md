# sources/user-network-fs/nfs-utils/support/include/nfsdnl.h

## Purpose
Declares a helper for sending simple string-attribute commands to the nfsd generic netlink family.

## Important APIs, Types, and Functions
`nfsd_nl_cmd_str(cmd, attr, value)` is real when `HAVE_NFSD_NETLINK` is enabled and an inline `-ENOSYS` stub otherwise.

## Control Flow
Callers issue one nfsd netlink command carrying one string attribute, wait for ACK, and receive 0 or negative errno.

## State and Persistence Behavior
No state in the header. The implementation opens and closes netlink sockets per command.

## Dependencies and Integration Points
Used by nfsdctl/exportfs-style control code. Depends on nfsd netlink command and attribute constants.

## Risks and Edge Cases
Callers must handle `-ENOSYS` when netlink support is absent and negative errno when the family or command is unsupported.

## Test Signals
Build both netlink-enabled and disabled configurations and test command success, unknown family/attr, and ACK error paths.
