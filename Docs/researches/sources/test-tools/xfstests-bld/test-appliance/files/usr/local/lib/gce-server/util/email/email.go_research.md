# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email.go

Purpose: SendGrid-backed plain-text email sender and panic failure reporter for KCS/LTM.

Important APIs: `Send(subject, content, receivers)` and deferred `ReportFailure(log, logFile, email, subject)`.

Control flow: `Send` splits comma-separated recipients, loads `SENDGRID_API_KEY` and optional `GCE_REPORT_SENDER`, builds a SendGrid v3 mail with plain text content, sends, and treats only 2xx responses as success. `ReportFailure` recovers panics, logs stack trace, builds a message from panic content, syncs and appends the associated log file if available, and calls `Send`.

State and dependencies: GCE config secrets, SendGrid client, logrus log files, and `check.FileExists`.

Risks and test signals: `logging.GetFile` can return nil for non-file outputs, but the code dereferences it; most callers use file-backed logs. Recipients are not trimmed. Tests should mock SendGrid or use appliance-only integration; current test requires LTM/KCS host config.
