# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/email/email_test.go

Purpose: appliance integration test for the email utility.

Important flow: skip unless hostname is `xfstests-ltm` or `xfstests-kcs`; read `GCE_REPORT_EMAIL` from config; call `email.Send("test", "test msg", receiver)` and fail on errors.

State and dependencies: requires real GCE config and SendGrid API key, and sends a real email.

Integration points: confirms production credentials and SendGrid connectivity in a live appliance environment.

Risks and test signals: not suitable for regular CI because it is side-effecting and environment-gated. It does not test `ReportFailure`, recipient parsing, or non-2xx responses.
