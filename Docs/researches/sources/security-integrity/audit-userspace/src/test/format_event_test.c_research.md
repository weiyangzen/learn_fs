<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/format_event_test.c -->
# sources/security-integrity/audit-userspace/src/test/format_event_test.c

**Purpose**
This regression test checks that auditd event formatting emits enriched output that is longer than raw output and includes the audit interpretation separator plus an AUID interpretation.

**Important APIs, Types, And Functions**
The test initializes a `daemon_conf`, calls `init_event`, creates `auditd_event` objects with `create_event`, formats them with `format_event`, and releases them with `cleanup_event`. It defines the daemon-global `stop`, a dummy `update_report_timer`, and link stubs for `send_audit_event` and `distribute_event`.

**Control Flow**
The same trusted application audit message is formatted twice. First, `conf.log_format = LF_RAW` records the raw formatted message length. Second, `LF_ENRICHED` formats a fresh event and records the enriched length. The test then checks that enriched output is longer, that byte offset 95 is `AUDIT_INTERP_SEPARATOR`, and that text after that point contains `AUID`.

**State And Persistence**
The test uses only heap-allocated event state and daemon formatting globals initialized by `init_event`; it writes diagnostic output to stdout/stderr but no durable files.

**Dependencies And Integration Points**
It compiles daemon event, reconfigure, config, sendmail, dispatch, optional listen, libaudit, auparse, audisp, libev, and common code together. This makes it a high-integration test rather than a narrow unit test.

**Risks**
The separator check hard-codes offset 95 and the source comment warns the test message must stay in sync with that offset. Changes to audit formatting that are semantically correct can break this brittle index.

**Test Signals**
Failure indicates enriched formatting regressed, audit interpretation placement changed unexpectedly, or required auditd event initialization/link dependencies are broken.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/format_event_test.c -->
