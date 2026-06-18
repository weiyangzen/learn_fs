<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go

This file holds shared Kopia CLI connection logic for snapshotter and legacy persister adapters. `kopiaConnector` stores a `kopiarunner.KopiaSnapshotter`, server command, server address, server fingerprint, and function hooks for repository initialization modes.

Initialization chooses behavior from env such as engine mode and S3 bucket settings. It can connect/create filesystem or S3 repositories, optionally through a Kopia server. Client/server helpers authorize clients and connect clients using fingerprints. Function fields let persisters override server initialization when they do not support server mode.

State includes process-local Kopia config directories, server process handles, and repository connection details. Dependencies are `kopiarunner`, `os/exec`, and env-driven mode selection. Risks include env misconfiguration, argument order mistakes for filesystem-with-server paths, server lifecycle leaks, and hidden coupling to default host/user constants. Tests use a stub connector to validate mode dispatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go -->
