# sources/object-store/daos/src/vos/storage_estimator/common/parse_csv.py

## Purpose
Implements the storage estimator CSV ingestion command. It converts one-row CSV summary data into an `AverageFS` model, dumps YAML, and runs the normal YAML processing pipeline.

## Important APIs, Types, And Functions
`FILE_SIZES` defines supported size buckets. `ProcessCSV` extends `ProcessBase`; `run` coordinates ingest, YAML dump, output creation, and processing. `_ingest_csv` parses fields, computes average directory/symlink/file sizes, configures `AverageFS`, reads live DFS inode metadata through `get_dfs_inode_akey`, and adds file buckets.

## Control Flow
The parser reads exactly two CSV lines: header and values. It validates equal field/value counts, extracts known fields with defaults, computes unknown item count for logging, initializes `AverageFS` from CLI object class/settings, and iterates `FILE_SIZES` to add average file objects for nonzero buckets.

## State And Persistence
`run` writes the generated YAML to `args.output` through `ProcessBase._create_file`; ingest itself returns an in-memory `AverageFS`.

## Dependencies And Integration
Depends on `dfs_sb.get_dfs_inode_akey`, `explorer.AverageFS`, and `util.ProcessBase`. Used by `daos_storage_estimator.py read_csv` and tests.

## Risks
Only one row of values is accepted. `items_per_dir` is computed but unused. `count_dir` defaults to one but a CSV value of zero causes division by zero. Live DFS inode discovery requires DAOS libraries unless tests patch/provide an environment. Error message concatenation lacks spaces before count details.

## Test Signals
`CSVTestCase` validates generated aggregate stats for SX, RP_3GX, and EC_16P2GX using `test_data.csv` and golden YAML files. Shell smoke tests run read_csv with multiple object classes, checksums, and aggregation.
