# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconConstants.java

## Purpose
`ReconConstants` collects stable filenames, query parameter names, default values, stats keys, size-bin bounds, and shared reprocess guards used across Recon.

## Important APIs, Types, And Functions
Important values include snapshot DB names, REST query parameter constants, file/container size bounds and bin counts, stat keys like `TOTAL_KEYS`, and atomic flags `FILE_SIZE_COUNT_TABLE_TRUNCATED` and `CONTAINER_KEY_MAPPER_INITIALIZED`. `resetTableTruncatedFlags()` clears both flags.

## Control Flow
There is no service flow beyond reset. Size-bin counts are calculated statically from power-of-two bounds.

## State And Persistence
Most values are immutable constants. The two `AtomicBoolean` fields are process-local coordination state used during OM task reprocessing to prevent duplicate truncation or initialization.

## Dependencies And Integration Points
The constants are used by REST endpoints, Recon tasks, `ReconUtils`, schema/table writers, and snapshot handling. Query names define the public API contract.

## Risks
Changing constants affects REST compatibility and task persistence semantics. Atomic guards are JVM-local, so they coordinate concurrent tasks only within one Recon process and must be reset per reprocess cycle.

## Test Signals
Tests should validate size-bin count math, reset behavior, and endpoint defaults that depend on these constants.
