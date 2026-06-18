# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneUtils.java

## Purpose
`RewriteTablePathOzoneUtils` contains helper functions for the Ozone Iceberg rewrite action.

## Important APIs, types, and functions
`statsFileCopyPlan` pairs before/after `StatisticsFile` paths after validating equal count and size. `fileExist` handles blank/null paths and delegates to Iceberg `FileIO`. `getMetadataLocation` derives the metadata directory from current metadata file location. `checkNonNullNonEmpty` enforces non-null/non-blank strings. `saveFileList` writes copy pairs to `stagingDir + "file-list"`. `writeAsCsv` writes UTF-8 comma-separated pairs. `snapshotSet` returns metadata snapshots or an empty set.

## Control flow
The utility methods are stateless and fail fast on invalid invariants. CSV writing wraps IO failures as Iceberg `RuntimeIOException`.

## State and persistence behavior
Only `saveFileList`/`writeAsCsv` persist data, creating or overwriting the file-list output through Iceberg `OutputFile`.

## Dependencies and integration points
The action uses these helpers for validation, staging defaults, statistics copy planning, and final copy-plan persistence.

## Risks and edge cases
CSV output does not escape commas in paths. `getMetadataLocation` requires a file separator in metadata file location. Stats-file pairing is positional and assumes Iceberg preserves list order after path replacement.

## Test signals
Tests cover empty stats, mismatched count, mismatched size, valid path pairs, default staging metadata location, and file-list parsing.
