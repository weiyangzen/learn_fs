# sources/storage-engines/foundationdb/fdbclient/BulkDumping.cpp

Purpose: This small file provides the construction entry point for bulk dump jobs in fdbclient. It converts caller-supplied range, job root, bulk load type, and transport method into a `BulkDumpState`.

Important APIs and types: It includes `fdbclient/BulkDumping.h` and implements `createBulkDumpJob(const KeyRange& range, const std::string& jobRoot, const BulkLoadType& type, const BulkLoadTransportMethod& transportMethod)`. The return type is `BulkDumpState`.

Control flow: The function has no branching or side effects. It returns `BulkDumpState(range, type, transportMethod, jobRoot)`, preserving the caller-provided values while matching the constructor's argument order.

State and persistence behavior: No state is persisted in this file. Any durable job metadata, dump manifest, or transport-specific state is owned by `BulkDumpState` and downstream bulk load/dump code.

Dependencies and integration points: This file is a thin linkage point for code that wants to create bulk dump jobs without directly invoking the `BulkDumpState` constructor. Snapshot manifest support in `BackupContainerFileSystem.cpp` recognizes bulkdump metadata, so this function is part of the broader backup and bulk-load ecosystem even though it does not touch containers directly.

Risks: The main risk is constructor-order drift: if `BulkDumpState` changes, this wrapper must be updated so `jobRoot`, type, and transport do not get misbound. Because it performs no validation, callers or `BulkDumpState` must reject invalid ranges, empty roots, or unsupported transport combinations.

Test signals: Tests should verify that a created job preserves the key range, root path, bulk load type, and transport method. Integration signals come from bulk dump snapshot manifests and restore/import workflows that consume `BulkDumpState`.
