# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h` is a 149-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `TEST`, `TST_EXP_PASS_SILENT`; local functions: `check_support_cmd`, `check_qoff`, `check_qon`, `check_qoffv`, `check_qonv`, `check_qlim`; struct/table types referenced: `struct fs_disk_quota`, `struct fs_quota_statv`, `struct fs_quota_stat`; important macros/constants: `QUOTACTL02_H`, `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `check_support_cmd`, `check_qoff`, `check_qon`, `check_qoffv`, `check_qonv`, `check_qlim`.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<unistd.h>`, `<stdio.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`, `<xfs/xqm.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.d_rtb_softlimit`, `.d_fieldmask`, `.qs_version`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `quotactl_syscall_var.h`; `do_quotactl() to %s`; `xfs quota enforcement was on unexpectedly`; `quotactl() succeeded to %s`; `xfs quota enforcement was off unexpectedly`.
