## sources/sync-backup/syncthing/lib/osutil/osutil_test.go

Purpose: tests deletion detection, rename/copy semantics, and IP string parsing.

Important tests: `TestIsDeleted` checks missing, present, and error cases. `TestRenameOrCopy` creates source/destination fake filesystems, exercises `RenameOrCopy`, and verifies destination data and source removal. `TestIPFromString` checks host:port and raw IP parsing.

Control flow and state: tests create temporary fake or OS-backed paths, mutate files, call osutil helpers, and assert final filesystem state.

Dependencies and integration points: validates helpers used by model pullers and network/NAT code.

Risks: fake filesystem tests may not capture all OS rename/copy edge cases. IP parsing tests are narrow.

Test signals: solid smoke coverage for core file helper semantics.
