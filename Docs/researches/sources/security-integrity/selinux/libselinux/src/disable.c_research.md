# sources/security-integrity/selinux/libselinux/src/disable.c

Purpose: Requests SELinux disablement by writing to `selinuxfs/disable`.

Important APIs/types/functions: `security_disable()` writes `"1"` to `selinux_mnt/disable`.

Control flow: requires `selinux_mnt`, opens the disable node write-only, writes a one-character string, closes, and returns success if write succeeded.

State and persistence: this is a persistent/security-critical kernel state change when supported by the kernel and policy mode.

Dependencies and integration: depends on `selinuxfs` exposing a writable `disable` node.

Risks and test signals: this API has high operational impact. Tests should mock or sandbox the filesystem node, cover missing mount, read-only/permission failure, partial writes, and descriptor close.
