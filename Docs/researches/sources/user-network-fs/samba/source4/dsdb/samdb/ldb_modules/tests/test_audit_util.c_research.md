# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_audit_util.c

Purpose: This cmocka file directly includes `../audit_util.c` and validates shared helper behavior used by DSDB audit modules. It covers attribute/value JSON encoding, redaction, LDB/session metadata extraction, operation naming, DN extraction, remote address formatting, and modify-action naming.

Important APIs, types, and functions: The tests call `dsdb_audit_add_ldb_value`, `dsdb_audit_attributes_json`, `dsdb_audit_get_remote_address`, `dsdb_audit_get_ldb_error_string`, `dsdb_audit_get_user_sid`, `dsdb_audit_get_actual_sid`, `dsdb_audit_is_system_session`, `dsdb_audit_get_unique_session_token`, `dsdb_audit_get_actual_unique_session_token`, `dsdb_audit_get_remote_host`, `dsdb_audit_get_primary_dn`, `dsdb_audit_get_message`, `dsdb_audit_get_secondary_dn`, `dsdb_audit_get_operation_name`, `dsdb_audit_get_modification_action`, `dsdb_audit_is_password_attribute`, and `dsdb_audit_redact_attribute`.

Control flow: Value serialization tests feed null blobs, printable strings, non-printable data, exactly `MAX_LENGTH` data, and over-limit data into JSON arrays, asserting null encoding, base64 markers, truncation markers, and value contents. Attribute JSON tests compare add versus modify action labels and verify secret attributes are redacted. Session tests progressively populate LDB opaque session data and security tokens, checking null behavior, first-SID selection, system SID detection, and GUID extraction. Request tests switch `req->operation` across add, modify, delete, rename, extended, register-control, register-partition, and unknown cases to validate DN/message/operation helpers.

State and persistence behavior: The file creates only transient LDB contexts, modules, requests, messages, socket addresses, auth sessions, and JSON objects. LDB opaque slots such as `remoteAddress`, `DSDB_SESSION_INFO`, and `DSDB_NETWORK_SESSION_INFO` are the key state carriers.

Dependencies and integration points: It depends on Samba JSON helpers, talloc, LDB private request structures, socket address formatting, SID/GUID helpers, and the audit utility implementation. These helpers are integration points for both general audit logging and group audit logging.

Risks: The value-formatting tests lock in truncation and base64 behavior; changing `MAX_LENGTH` or printable-character rules affects audit consumers. Session tests reveal a subtle behavior: a zeroed `auth_session_info` can still yield a non-null unique session token pointer with undefined contents, which callers must treat carefully.

Test signals: Passing tests signal that audit helpers produce stable JSON for attribute data, redact sensitive attributes, correctly derive request DNs and names, and tolerate absent session/remote metadata without crashing.
