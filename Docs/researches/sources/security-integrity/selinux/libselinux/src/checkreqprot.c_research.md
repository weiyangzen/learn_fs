# sources/security-integrity/selinux/libselinux/src/checkreqprot.c

Purpose: Reads the kernel SELinux `checkreqprot` setting.

Important APIs/types/functions: `security_get_checkreqprot()` opens `selinux_mnt/checkreqprot`, reads a small text integer, parses it with `sscanf`, and returns the value.

Control flow: missing `selinux_mnt`, open failures, read failures, and parse failures all return `-1`.

State and persistence: this is read-only kernel state.

Dependencies and integration: depends on `selinux_mnt` and the legacy `checkreqprot` selinuxfs node.

Risks and test signals: tests should cover absent node on newer systems, non-integer contents, and normal `0`/`1` values.
