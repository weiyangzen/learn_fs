# sources/storage-engines/rocksdb/java/spotbugs-exclude.xml

## Purpose
This XML file is the SpotBugs exclusion baseline for RocksJava. It suppresses known or accepted static-analysis findings so builds can focus on unsuppressed regressions.

## Important APIs, Types, and Functions
The file uses SpotBugs `FindBugsFilter` syntax with repeated `Match` blocks. It suppresses patterns such as `UPM_UNCALLED_PRIVATE_METHOD`, `MS_EXPOSE_REP`, `EI_EXPOSE_REP`, `EI_EXPOSE_REP2`, `BIT_IOR_OF_SIGNED_BYTE`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD`, and `DMI_HARDCODED_ABSOLUTE_FILENAME`. It targets classes including callback bridge classes, options/descriptors, metadata DTOs, transaction info classes, iterator write entries, and backup/statistics/range wrappers.

## Control Flow
There is no runtime control flow. SpotBugs consumes the filter during static analysis and omits matching warnings. A commented-out `TransactionDB$KeyLockInfo` exclusion is retained as a way to test that CI reports a consequent SpotBugs error.

## State and Persistence Behavior
The file persists static-analysis policy, not application state. It influences CI and local analysis outcomes.

## Dependencies and Integration Points
It integrates with the Java build's SpotBugs configuration. The exclusions reflect JNI and wrapper patterns where private methods are invoked from native code or arrays are intentionally exposed for performance/API compatibility.

## Risks and Edge Cases
Broad suppressions, especially class-level or pattern-only matches, can hide real defects. The header comments say the baseline should be justified or removed, indicating technical debt. Duplicate `BackupEngineOptions` entries suggest the file may need cleanup.

## Test Signals
Static-analysis tests should confirm that removing the documented test exclusion produces a SpotBugs error. Maintenance should review whether each exposed-representation suppression is still required and whether JNI callback private methods are better annotated or configured.
