# sources/sync-backup/borg/src/borg/archiver/analyze_cmd.py

## Purpose
This command module implements `borg analyze`, which compares consecutive selected archives and reports directory paths with the largest amount of chunk churn. It helps users find hot spots such as caches, temporary directories, or high-change data that may need exclusion or recreation.

## Important APIs, Types, and Functions
- `ArchiveAnalyzer.__init__(args, repository, manifest)` stores the repository, manifest, args, and a `defaultdict(int)` mapping directory path to cumulative changed chunk size.
- `analyze()` logs start/end, runs archive analysis, and prints the report.
- `analyze_archives()` obtains selected archives through `manifest.archives.list_considering(args)`, requires at least two, iterates archives in order, and compares adjacent archive chunk maps.
- `analyze_archive(id)` opens an `Archive`, iterates items, and builds `directory_path -> {chunk_id: plaintext_size}` for file items.
- `analyze_change(base, new)` adds sizes for chunk ids added or removed per directory.
- `report()` prints a sorted descending text report.
- `AnalyzeMixIn.do_analyze` is decorated with `with_repository(compatibility=(Manifest.Operation.READ,))`.
- `build_parser_analyze()` registers the `analyze` subcommand and shared archive filters.

## Control Flow
The command opens a read-compatible repository and manifest through `_common.with_repository`. It selects archives with standard archive filter arguments, analyzes the first as the base, then for each subsequent archive builds a new per-directory chunk map and compares it with the previous one. The comparison is adjacent-pair based, so churn accumulates across the selected time series.

## State and Persistence Behavior
`borg analyze` is read-only. It reads archive metadata and item streams, but it does not write repository, manifest, cache, or filesystem state. Its only persistent-like output is terminal output; in-memory state is `difference_by_path` and per-archive chunk maps.

## Dependencies and Integration Points
It depends on `_common.with_repository`, `_common.define_archive_filters_group`, `Archive`, `Manifest`, `Repository`, `ProgressIndicatorPercent`, and helper formatting/logging. It integrates with the archive item model (`item.chunks` as chunk id/size entries) and the same archive selection options used by list/check/info-like commands.

## Risks and Edge Cases
- It uses plaintext chunk sizes, not compressed repository object sizes, so results approximate logical churn rather than storage impact.
- It groups by direct parent directory only, not recursive subtree aggregation.
- The nested `analyze_path_change` uses the outer `directory_path` variable rather than its `path` parameter; because calls pass the same variable name, behavior is currently correct but fragile under refactoring.
- Large archive series can require significant metadata reads and memory for per-directory chunk maps.
- Chunks reused across files/directories are represented in per-directory dicts, so duplicate chunks within the same directory collapse by id.

## Test Signals
Tests should create multiple archives with controlled file additions/removals/modifications and verify reported directory churn ordering and sizes. Edge coverage should include fewer than two archives, archive filters selecting no/one archive, repeated chunks, files in repository root, and large archives to watch performance/progress behavior.
