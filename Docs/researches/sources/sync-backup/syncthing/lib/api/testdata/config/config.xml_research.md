# sources/sync-backup/syncthing/lib/api/testdata/config/config.xml

Purpose: Test fixture configuration used as API test config base directory.

Important data: Defines configuration version 28 with two folders, multiple devices, GUI settings, LDAP placeholder, and options. It includes localhost device addresses, GUI address `127.0.0.1:8081`, user/password/API key values for tests, disabled global announce, enabled local announce, and a folder ID containing non-ASCII characters to exercise encoding paths.

Control flow: Not executable. It is loaded by config code during tests after `TestMain` points `locations.ConfigBaseDir` at `testdata/config`.

State and persistence behavior: Static fixture on disk. Tests may read it as initial config input but should avoid mutating the source fixture.

Dependencies and integration points: Used by `api_test.go` through Syncthing locations/config loading. The GUI API key and bcrypt password support auth-related test scenarios.

Risks: Fixture drift can change API test assumptions. Embedded credentials are test-only but still should not be copied into production examples. Non-ASCII content is intentional and should be preserved.

Test signals: Supports endpoint tests requiring realistic folders, devices, GUI config, and options.
