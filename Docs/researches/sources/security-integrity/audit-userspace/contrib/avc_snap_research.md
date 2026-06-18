# sources/security-integrity/audit-userspace/contrib/avc_snap

Purpose: Legacy Python 2 audisp-style SELinux AVC analyzer that reads audit messages from stdin, groups records by audit event signature, and dispatches AVCs to setroubleshoot plugins.

Important APIs and types: Defines class `avc_snap` with `audit_list`, `cur_sig`, and loaded `plugins`. Uses Python modules `audit`, `avc`, `AuditMsg`, `syslog`, `select`, `struct`, and `setroubleshoot.signature.AVC`. Main methods are `is_avc`, `out`, `process`, and `run`.

Control flow: `run` waits on stdin with `select` for up to five seconds. When input arrives, it reads an `AuditMsg`, extracts type/body, and calls `process`. `process` splits the body, treats the first token as an event signature, flushes the previous event if the signature changes, and appends the remaining fields. `out` ignores non-AVC events and granted AVCs, translates denied AVC field lists via `avc.SERules`, builds an `AVC`, and calls plugin `analyze` and `report` until a plugin handles it. Timeouts flush pending grouped records.

State and persistence: State is in memory only and reset after every flush. Persistent effects come from setroubleshoot plugin reporting and syslog messages under the `avc_snap` ident.

Dependencies and integration: Intended to be launched by auditd/audisp as a stdin-fed plugin. It depends on obsolete Python 2 syntax, setroubleshoot libraries, SELinux AVC parsing, and audit message framing from `AuditMsg`.

Risks: Python 2 exception syntax makes it incompatible with Python 3. Event grouping assumes `data_list[0]` exists and is a stable signature. It drops granted AVCs. Broad exception handling logs but may hide plugin failures. If stdin feeds malformed messages, `struct.error` exits the daemon loop.

Test signals: Feed raw AVC audit streams into stdin and verify plugin reports, timeout flushing, signature-boundary flushing, syslog error handling, and ignoring of `granted` AVC records. Python 2 runtime availability is itself a deployment signal.
