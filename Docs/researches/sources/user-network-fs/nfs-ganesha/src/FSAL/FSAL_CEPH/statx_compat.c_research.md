# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.c

## Purpose

`statx_compat.c` provides fallback implementations for Ceph FSAL low-level wrappers when libcephfs does not expose the newer statx-style API (`USE_FSAL_CEPH_STATX` disabled). It converts POSIX `struct stat` results into the local `struct ceph_statx` compatibility shape. The complete 204-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `posix2ceph_statx`, `fsal_ceph_ll_walk`, `fsal_ceph_ll_getattr`, `fsal_ceph_ll_lookup`, `fsal_ceph_ll_mkdir`, optional `fsal_ceph_ll_mknod`, `fsal_ceph_ll_symlink`, `fsal_ceph_ll_create`, `fsal_ceph_ll_setattr`, and `fsal_ceph_readdirplus`.

## Control Flow

Each wrapper calls the older libcephfs low-level API with uid/gid credentials, receives POSIX stat data where applicable, and populates `ceph_statx`. `fsal_ceph_ll_setattr` converts the requested Ceph setattr mask back into a POSIX `struct stat`. `fsal_ceph_readdirplus` calls `ceph_readdirplus_r`; if `AT_NO_ATTR_SYNC` is absent it may issue a lookup to acquire an inode ref and refreshed attributes.

## State and Persistence Behavior

The file owns no persistent state. It affects persistent CephFS metadata only through `fsal_ceph_ll_setattr` and creation wrappers. Its main state behavior is compatibility preservation: callers elsewhere can use `ceph_statx` masks even when libcephfs only returned POSIX stat.

## Dependencies and Integration Points

Dependencies include older libcephfs APIs, POSIX stat/time fields, `timespec_to_nsecs`, and the declarations/macros in `statx_compat.h`. It is linked only for fallback builds and is used by export and handle code through uniform wrapper names.

## Risks and Edge Cases

Birth time is not populated from POSIX stat fallback but the mask claims basic stats plus version. `stx_version` is synthesized from ctime nanoseconds, which may not have the same semantics as true Ceph version/change attributes. The fallback credentials pass only caller uid/gid, not the full auxiliary group set available in newer `UserPerm` paths. Readdir behavior changes based on `AT_NO_ATTR_SYNC`, potentially causing extra lookups and inode references.

## Test Signals

Test signals include a build with `USE_FSAL_CEPH_STATX` disabled, lookup/getattr/create/mkdir/symlink parity with statx builds, setattr mask translation for size/mode/uid/gid/time, readdirplus inode reference handling, auxiliary-group permission differences, and NFS change attribute stability across metadata updates.
