# sources/object-store/minio/cmd/server-startup-msg_test.go

Purpose: This test file verifies endpoint-display normalization and smoke-tests the startup message printers against initialized test configuration.

Important APIs and types: Tests call `stripStandardPorts`, `printServerCommonMsg`, `printCLIAccessMsg`, and `printStartupMessage`. Setup helpers include `prepareFS`, `newTestConfig`, and `globalMinioDefaultRegion`.

Control flow: `TestStripStandardPorts` asserts that HTTP `:80` and HTTPS `:443` are stripped from a multi-endpoint list, malformed URLs are left unchanged, and non-standard scheme/port pairings are preserved. The print tests prepare a filesystem object layer, initialize test config, and call the printing functions with `http://127.0.0.1:9000`.

State and persistence behavior: The print tests create temporary filesystem state through `prepareFS`, initialize global MinIO test config, and remove the temp directory. The output itself is written to the startup logger and is not captured for content assertions.

Dependencies and integration points: The tests depend on server test helpers and global startup/config state. They exercise formatting functions without running a full server bootstrap.

Risks: The smoke tests primarily guard against panics, not exact logged content. Changes to terminal/color/global credential behavior may not be caught unless they affect execution. `TestStripStandardPorts` is the main functional assertion.

Test signals: Expected stripped endpoints, unchanged malformed/nonstandard endpoints, and successful execution of message printers after test config initialization.
