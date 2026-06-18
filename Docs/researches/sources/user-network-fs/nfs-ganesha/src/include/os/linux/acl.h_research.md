# sources/user-network-fs/nfs-ganesha/src/include/os/linux/acl.h

## Purpose
This Linux compatibility header fills gaps for non-standard POSIX ACL file-descriptor helpers when the platform ACL library lacks them.

## Important APIs, Types, And Control Flow
After including `config.h`, `<limits.h>`, `<sys/types.h>`, and `<sys/acl.h>`, it conditionally declares `acl_get_fd_np(int fd, acl_type_t type)` and `acl_set_fd_np(int fd, acl_t acl, acl_type_t type)` when `HAVE_ACL_GET_FD_NP` or `HAVE_ACL_SET_FD_NP` are absent.

## State And Persistence
The header has no state. The declared functions read and write POSIX ACLs on open file descriptors, which affects filesystem metadata when implemented and called.

## Dependencies And Integration Points
It integrates with POSIX ACL conversion code in `posix_acls.h`/implementation and with build-time feature detection in `config.h`. FSALs use this path to avoid path-based races when translating NFS ACLs.

## Risks And Test Signals
The main risks are mismatched fallback implementations and ACL type support differences between access and default ACLs. Test signals include build matrix coverage with and without native `_np` functions, descriptor ACL get/set round-trips, default ACL handling on directories, and error propagation for unsupported filesystems.
