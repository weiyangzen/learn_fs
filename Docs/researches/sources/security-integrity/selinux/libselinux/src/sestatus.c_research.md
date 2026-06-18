<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sestatus.c -->
# sources/security-integrity/selinux/libselinux/src/sestatus.c

## Purpose
Provides fast access to SELinux kernel status through the selinuxfs `status` mmap page, with optional netlink fallback.

## Important APIs, Types, And Functions
`struct selinux_status_t` mirrors the kernel status page. `selinux_status_open()`, `selinux_status_close()`, `selinux_status_updated()`, `selinux_status_getenforce()`, `selinux_status_policyload()`, and `selinux_status_deny_unknown()` expose status reads. Fallback callbacks update local enforcing and policyload counters from netlink events.

## Control Flow
Mapped-page reads use a seqlock pattern: wait for an even sequence, read fields, and retry if the sequence changes. `selinux_status_updated()` triggers AVC callbacks when enforcing or policyload changes since the previous call.

## State And Persistence Behavior
State is process-global: mapped status pointer, last sequence/policyload, fallback counters, and optional fallback netlink thread. It is read-only with respect to kernel state.

## Dependencies And Integration Points
Uses `selinux_mnt`, AVC internal callbacks, netlink open/check/loop helpers, `avc_using_threads`, and memory barriers.

## Risks And Test Signals
Risks include fallback policyload unreliability before first event, thread shutdown, seqlock correctness, and global open/close lifecycle. Tests should cover mmap success, mmap failure with fallback, no fallback, sequence changes, enforcing callbacks, policyload callbacks, and deny_unknown reading.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sestatus.c -->
