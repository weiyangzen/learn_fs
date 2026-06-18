<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpolicyload.c -->
# sources/security-integrity/selinux/libselinux/utils/getpolicyload.c

## Purpose
Prints the kernel policyload counter from the SELinux status page.

## Important APIs, Types, And Functions
Calls `selinux_status_open(0)`, `selinux_status_policyload()`, prints the integer, and closes status.

## Control Flow
Netlink fallback is intentionally disabled because policyload fallback is unreliable until an event arrives.

## State And Persistence Behavior
Read-only mmap/status access with temporary process-global status handle.

## Dependencies And Integration Points
Exercises `sestatus.c` mapped-page path.

## Risks And Test Signals
Test status map available/unavailable, read errors, and cleanup after failed open/read.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpolicyload.c -->
