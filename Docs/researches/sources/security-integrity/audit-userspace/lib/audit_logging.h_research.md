# sources/security-integrity/audit-userspace/lib/audit_logging.h

Purpose: Public header for libaudit connection lifecycle and standardized audit logging helper APIs.

Important declarations: Declares `audit_open`, `audit_close`, value encoding helpers, `audit_encode_nv_string` with deallocation annotation, and message logging functions for generic user messages, command messages, account changes, user AVCs, SELinux management, and user commands.

Control flow: Header-only declarations with C++ linkage guards and fallback attribute macro definitions.

State and persistence: No state itself. Declared functions send persistent audit records to the kernel and may log errors.

Dependencies and integration: Includes `<features.h>`, `<sys/types.h>`, and `<audit-records.h>`. Included by `libaudit.h` and installed as a public API header.

Risks: Public ABI and source compatibility constraints are high. Attribute macros must be safe on non-glibc systems. The header must remain self-contained after installation.

Test signals: C and C++ compile tests including only `audit_logging.h`, ABI symbol checks, and static analyzer validation for annotated buffer/deallocation functions.
