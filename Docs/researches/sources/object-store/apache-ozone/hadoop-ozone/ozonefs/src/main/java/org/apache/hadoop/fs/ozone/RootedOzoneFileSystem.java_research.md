<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Main unshaded full rooted OFS implementation with tracing around lease recovery and file-closed checks.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem`, implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`, manages storage statistics, creates `RootedOzoneClientAdapterImpl`, wraps streams with capability classes, and implements traced `recoverLease`/`isFileClosed`.

## Control flow
`recoverLease` opens an `ofs recoverLease` tracing span and delegates to `recoverLeaseTraced`, which sets the path attribute, prepares recovery, handles already-closed keys, finalizes block lengths, builds `OmKeyArgs`, and commits recovery. `isFileClosed` opens an `ofs isFileClosed` span, sets an operation attribute, increments write ops, and delegates to the adapter.

## State and persistence behavior
Local state is statistics and force-recovery flag. Persistent effects are inherited filesystem mutations, recovery commits, and safe-mode changes. File-closed checks are read-like but increment write ops in this main-module implementation.

## Dependencies and integration points
Integrates rooted filesystem behavior with OpenTelemetry tracing, key providers, lease recovery, storage statistics, and path capability helper.

## Risks and test signals
The write-op increment in `isFileClosed` may be intentional or a metrics bug compared with other variants. Tests should assert tracing attributes where supported, recovery semantics, stats deltas, and parity with `ozonefs-hadoop3` unless divergence is deliberate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
