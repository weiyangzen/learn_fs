# sources/security-integrity/selinux/libselinux/src/deny_unknown.c

Purpose: Reads the kernel policy setting controlling whether unknown classes or permissions are denied.

Important APIs/types/functions: `security_deny_unknown()` opens `selinux_mnt/deny_unknown`, reads a small integer string, parses it, and returns the value.

Control flow: missing mount, open error, read error, or parse failure returns `-1`.

State and persistence: read-only kernel policy state.

Dependencies and integration: used by high-level access checking to decide whether unknown class/permission names should fail closed or be allowed.

Risks and test signals: tests should cover absent file, malformed content, and both deny/allow configurations.
