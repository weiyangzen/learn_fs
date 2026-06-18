# sources/object-store/rustfs/crates/heal/tests/endpoint_index_test.rs

This integration test validates endpoint index setup for local ECStore disks. It creates a `TempDir`, four disk directories, converts each into an `Endpoint`, sets pool/set/disk indexes, builds `PoolEndpoints` and `EndpointServerPools`, asserts indexes are correct, initializes local disks, and constructs an `ECStore`.

The test persists only temporary filesystem state and does not create object data. Its integration value is confirming endpoint metadata survives the path-to-endpoint and pool-construction flow that heal event conversion and set disk ID generation rely on.

Dependencies include ECStore endpoint types, `tempfile`, `SocketAddr`, Tokio, and `CancellationToken`. It is a positive-path signal for valid indexes; invalid endpoint-index handling is covered by bug-fix tests.
