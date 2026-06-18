<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_netlink.h -->
# sources/security-integrity/selinux/libselinux/src/selinux_netlink.h

## Purpose
Defines SELinux netlink notification constants and message payload structures.

## Important APIs, Types, And Functions
Declares message IDs `SELNL_MSG_SETENFORCE`, `SELNL_MSG_POLICYLOAD`, multicast groups `SELNL_GRP_AVC`, and payload structs `selnl_msg_setenforce` and `selnl_msg_policyload`.

## Control Flow
No executable code.

## State And Persistence Behavior
No state. The structures describe kernel-to-userspace notification data.

## Dependencies And Integration Points
Consumed by AVC/netlink code and status fallback handling for setenforce and policyload events.

## Risks And Test Signals
ABI compatibility with kernel headers is the main risk. Compile checks and netlink event integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_netlink.h -->
