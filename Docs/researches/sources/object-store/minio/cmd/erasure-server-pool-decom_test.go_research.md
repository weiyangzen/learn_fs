# sources/object-store/minio/cmd/erasure-server-pool-decom_test.go

## Purpose
This handwritten test file exercises decommission pool metadata validation. It builds temporary two-pool erasure setups and checks whether `poolMeta.validate` asks for metadata updates under different pool membership and decommission-state scenarios.

## Important APIs, Types, and Functions
`prepareErasurePools` creates 32 temporary disks, splits them into two 16-drive endpoint pools, initializes an object layer, and returns the object layer plus directories for cleanup.

`TestPoolMetaValidate` extracts baseline `poolMeta` and `serverPools`, creates a second independent object layer to represent changed pool command lines, builds reduced and reordered pool lists, creates variants where pool 0 has completed or pending decommission, and runs table-driven assertions against `poolMeta.validate`.

## Control Flow
The test creates one initial erasure-pool object layer, defers disk cleanup, then creates a second object layer to simulate a new pool layout. It builds `nmeta1` with completed decommission on pool 0 and `nmeta2` with non-completed decommission on pool 0.

The table covers unchanged layout, changed pool identity, reduced pool count, order change, completed pool still present, pending decommission still present, pending pool removed, completed pool removed, fresh empty metadata, and order change with pending decommission. Each subtest calls `validate` and checks `update` plus error presence.

## State, Dependencies, Risks, and Test Signals
The test does not write or reload `pool.bin` directly, but it exercises the decision that controls whether a loaded `poolMeta` is accepted as-is or rewritten by `newPoolMeta`.

It depends on local disk helpers, endpoint builders, object-layer initialization, and concrete `erasureServerPools` internals. It is closer to an integration test than a pure unit test.

Some table names say "Invalid" while `expectedErr` is false. Current `validate` behavior signals rewrite needs through `update` and logging, not errors. The file does not validate decommission queue behavior, resume markers, object migration, final verification, cancel/fail/complete APIs, or logged warnings.
