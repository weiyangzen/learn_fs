# sources/security-integrity/selinux/libselinux/src/getenforce.c

Purpose: Reads current SELinux enforcing mode from `selinuxfs/enforce`.

Important APIs/types/functions: `security_getenforce()` returns booleanized parsed integer value.

Control flow: opens the enforce file, reads up to 19 bytes, parses an integer with `sscanf`, and returns `!!enforce`.

State and persistence: read-only kernel state.

Dependencies and integration: AVC initialization and password-access checks use it to determine permissive behavior.

Risks and test signals: tests should cover missing mount, unreadable file, malformed content, and nonzero values mapping to `1`.
