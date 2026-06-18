# sources/user-network-fs/rclone/cmd/ncdu/scan/scan_test.go

Purpose: unit-tests ncdu scan tree construction, aggregate attributes, unknown-size behavior, read-error propagation, modtime access, and in-memory removal updates.

Important helpers/tests: `indexByName`, `fileEntry`, `TestScan`, `TestAttrsAverageSize`, `TestNewDirSizeAndCount`, `TestNewDirUnknownSize`, `TestNewDirReadErrorSetsEntriesHaveErrors`, `TestAttrIFile`, `TestAttrIDirLoaded`, `TestAttrIDirUnloaded`, `TestAttrWithModTimeI`, and removal propagation tests.

Control flow/state: tests construct mock dirs/objects or scan local fixtures, then inspect `Dir` methods. Removal tests verify parent totals and entries mutate correctly.

Dependencies/integration: local backend, `fstest`, `mockdir`, `mockobject`, testify. Risks: some tests call unexported `newDir`, tightly coupling to implementation; `TestScan` depends on fixture layout from another command directory. Coverage is strong for scan invariants and regression-prone aggregate accounting.
