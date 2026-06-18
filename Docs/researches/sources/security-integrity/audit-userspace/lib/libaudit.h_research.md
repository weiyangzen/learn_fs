# sources/security-integrity/audit-userspace/lib/libaudit.h

Purpose: Primary public libaudit header declaring low-level audit ABI structures, dispatcher protocol structures, machine/failure enums, translation APIs, kernel control APIs, rule-building APIs, watch helpers, and capability helpers.

Important types and APIs: Defines `AUDIT_KEY_SEPARATOR`, audit filter compatibility macros, `AUDIT_INTERP_SEPARATOR`, `MAX_AUDIT_MESSAGE_LENGTH`, `struct audit_message`, `struct audit_reply`, `struct audit_dispatcher_header`, dispatcher protocol versions, `machine_t`, `auditfail_t`, `reply_t`, `rep_wait_t`, and declarations for all main libaudit functions. Includes `audit_logging.h`, making logging APIs available through this header.

Control flow: Header-only declarations and ABI definitions with C++ guards. Some macros provide fallback definitions for libc attribute annotations and newer audit filter constants.

State and persistence: No direct state, but declared APIs mutate kernel audit state, procfs loginuid/session state, and rule structures supplied by callers.

Dependencies and integration: Includes `<asm/types.h>`, `<stdint.h>`, socket/netlink headers, `<linux/audit.h>`, syslog, and `audit_logging.h`. Used by auditctl, auditd, plugins, PAM integrations, and downstream applications.

Risks: Explicit comments mark structures as external ABI; field layout and dispatcher header size/versioning are compatibility-critical. Public header must remain self-contained and cannot rely on private compatibility headers. Changes to enum values, structure layouts, or function signatures can break compiled applications.

Test signals: ABI compliance checks, C/C++ standalone compile, downstream application build tests, symbol/version checks, and struct size/layout tests for dispatcher protocol and audit reply/message structures.
