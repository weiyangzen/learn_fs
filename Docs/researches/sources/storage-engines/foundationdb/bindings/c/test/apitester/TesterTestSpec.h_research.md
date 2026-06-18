# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.h

## Purpose
Defines the in-memory model for API tester TOML files.

## Important APIs, types, and functions
`WorkloadSpec` stores workload `name` plus string options. `TestSpec` stores title, blocking/callback mode, buggify, multi-threading, external-thread callbacks, profiling, DB-per-transaction, cluster-file tampering, thread/database/client ranges, disable-client-bypass, knobs, and workloads. `readTomlTestSpec` is the parser entry point.

## Control flow
The defaults in this header control omitted TOML fields: callback futures, one FDB/client thread, one database, up to ten clients, and no special network behavior.

## State and persistence behavior
These structs are transient and own no FDB handles or files.

## Dependencies and integration points
Includes generated FDB API version information and is consumed by the TOML parser and main tester executable.

## Risks and test signals
Default changes alter many tests. Range fields are randomized at runtime, so repeated scenario runs are the coverage signal.
