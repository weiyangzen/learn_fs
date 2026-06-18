# sources/storage-engines/wiredtiger/test/suite/test_util13.py

## Purpose

`test_util13.py` validates `wt dump` and `wt load` preservation of non-default table configuration. It covers simple file, simple table, and complex table/column-group datasets through scenarios.

## Important APIs, Types, and Functions

The class uses `SimpleDataSet`, `ComplexDataSet`, and `make_scenarios`. Helpers `compare_config`, `compare_files`, and `load_recheck` parse dump headers, compare expected config subsets, load dump output into a separate home, and dump again for comparison.

## Control Flow

`test_dump_config` populates the scenario dataset, writes an expected header containing the current WiredTiger version and expected config lines, runs `wt dump`, compares header/config fields, loads the dump into `dump_dir`, opens a new connection there, and re-dumps to verify configuration round-trips.

## State and Persistence Behavior

The test persists the original dataset, creates `expect.out`, `dump.out`, `dump_dir`, and `newdump.out`, and relies on dump/load preserving schema metadata and data.

## Dependencies and Integration Points

Integrates with dataset helpers, `wiredtiger.wiredtiger_version`, the `wt dump`/`load` utilities, and metadata config serialization.

## Risks and Edge Cases

The config parser is deliberately simple and strips complex table `colgroups`/`columns`; nested config groups or format changes can break it. Expected dump text is version-sensitive and output-format-sensitive.

## Test Signals

Signals include matching dump header/config subset, successful `wt load`, successful cursor validation through `ds.check`, and matching re-dumped configuration.
