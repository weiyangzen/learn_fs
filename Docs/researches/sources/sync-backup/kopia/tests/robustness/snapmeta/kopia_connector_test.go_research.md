<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go

This file tests `kopiaConnector` mode dispatch with a `testConnector` stub. It configures connector function hooks, changes environment-like mode inputs, and verifies the expected filesystem/S3/server initialization path is called.

The control-flow signal is important because real connector methods launch Kopia commands and servers. The stub records which method was invoked, allowing tests to check dispatch without external binaries.

Risks covered are wrong mode routing and missing hook use. Risks not covered are actual Kopia command success, TLS fingerprint handling, server startup timing, and environment cleanup. Dependencies are `testify/require` and package-internal connector fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go -->
