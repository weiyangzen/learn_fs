# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/appends_test.go

Purpose: Tests append behavior for zonal-bucket unfinalized/finalized objects, including dual-mount takeover, visibility before/after close, concurrent append and `r+` handles, random-write fallback, stat-size refresh, and repeated reopen appends.

Important APIs/types/functions: Methods on `DualMountAppendsTestSuite` and `SingleMountAppendsTestSuite` use `createUnfinalizedObject`, `deleteUnfinalizedObject`, `operations.OpenFileInMode`, `appendToFile`, direct `client.ReadObjectFromGCS`, `operations.ValidateESTALEError`, `os.Stat`, and `syscall.O_DIRECT`.

Control flow: tests create an object, open append and sometimes `r+` handles, perform writes, then validate either immediate backend visibility for append-session behavior or delayed visibility until close for fallback writes. Dual-mount takeover verifies old handle sync/close becomes stale after a secondary mount writes. Stat tests validate kernel-visible size before and after metadata-cache expiry.

State/persistence: Maintains `t.fileName` and `t.fileContent` as suite state. Direct GCS reads are the durable source of truth. Open file handles intentionally hold unfinalized append sessions.

Dependencies/integration: Depends on rapid-appends suite setup, zonal bucket support, GCS client helpers, and operation helpers.

Risks/test signals: Timing around stat cache expiry and flush duration can be slow/flaky. Passing signals append-session invalidation, close-time persistence, fallback semantics, and kernel stat refresh work for zonal rapid appends.
