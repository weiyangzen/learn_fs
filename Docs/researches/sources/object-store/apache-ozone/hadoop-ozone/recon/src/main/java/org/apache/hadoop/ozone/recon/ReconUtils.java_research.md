# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconUtils.java

## Purpose
`ReconUtils` is a broad utility class for Recon filesystem paths, snapshot archive handling, FSO path reconstruction, metadata table pagination, global stats writes, metrics extraction, CSV streaming, and utilization size-bin math.

## Important APIs, Types, And Functions
Key APIs include `getReconDbDir`, `createTarFile`, `untarCheckpointFile`, `constructFullPath`, `constructFullPathPrefix`, `convertToObjectPathForOpenKeySearch`, `makeHttpCall`, `getLastKnownDB`, `upsertGlobalStatsTable`, permission conversion helpers, size-bin helpers, `isInitializationComplete`, `convertToEpochMillis`, `validateStartPrefix`, `extractKeysFromTable`, `gatherSubPaths`, `validateNames`, `constructObjectPathWithPrefix`, `getMetricsData`, `extractLongMetricValue`, and `downloadCsv`.

## Control Flow
Path construction walks `NSSummary` parents bottom-up until parent ID zero, returning empty when the summary tree is missing/rebuilding. Object-path conversion parses volume/bucket/path names, resolves IDs from OM tables, then checks directory and open-file tables. Table extraction seeks by `prevKey` or prefix and iterates until limit or prefix mismatch. Snapshot selection picks the newest timestamped file and deletes older/unknown entries.

## State And Persistence
The class is mostly stateless aside from a replaceable static logger. It creates/deletes tar/snapshot files, deletes stale DB snapshot directories, writes global stats via DAO upsert, and streams CSV responses.

## Dependencies And Integration Points
It touches HDDS/SCM utilities, OM metadata tables, Recon namespace summary, Recon SCM facade, jOOQ/global stats DAO, Hadoop URL connections, CSV printer, and JAX-RS responses.

## Risks
The class mixes unrelated responsibilities. `getLastKnownDB` deletes files while scanning. Path conversion returns original prefixes on runtime failures, which can mask data issues. Name validation is bucket/volume-specific but used in path conversion. CSV and JSON callers must handle unescaped or large output carefully.

## Test Signals
Strong tests cover FSO path reconstruction, rebuild/missing summary behavior, object path conversion at root/volume/bucket/dir/key levels, table pagination, size-bin boundaries, date parse fallback, metrics parsing, global stats upsert, snapshot cleanup, and CSV headers/body.
