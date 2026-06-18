<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/audit.go -->
# sources/security-integrity/audit-userspace/bindings/golang/audit.go

Purpose: small cgo package exposing a limited libaudit logging API to Go.

Important APIs and functions: exports constants for virtualization audit event types and functions `AuditValueNeedsEncoding`, `AuditEncodeNVString`, and `AuditLogUserEvent`. C bindings include `libaudit.h`, `unistd.h`, `stdlib.h`, `string.h`, and use `pkg-config: audit`.

Control flow and state: each function converts Go strings to C strings and frees them. `AuditLogUserEvent` opens an audit fd, logs a user message with boolean result mapped to 1/0, closes the fd, and returns the cgo error; if `audit_open` fails it returns nil.

Dependencies and integration: relies on libaudit C APIs `audit_value_needs_encoding`, `audit_encode_nv_string`, `audit_open`, and `audit_log_user_message`.

Risks and test signals: `AuditLogUserEvent` swallowing `audit_open` failure as nil can hide logging failure. cgo allocation/free correctness is central; `AuditEncodeNVString` assumes libaudit returns malloc-owned memory. Only the disabled Go test covers encoding behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/audit.go -->
