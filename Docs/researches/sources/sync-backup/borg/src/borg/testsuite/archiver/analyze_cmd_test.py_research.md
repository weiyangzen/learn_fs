# sources/sync-backup/borg/src/borg/testsuite/archiver/analyze_cmd_test.py

Purpose: integration test for `borg analyze`, ensuring it reports cumulative chunk-change contribution for a path across archive history.

Important APIs/types/functions: `test_analyze` uses `cmd`, `RK_ENCRYPTION`, and `generate_archiver_tests` in local mode. Nested helpers create an archive named `archive` repeatedly and run `analyze -a archive`.

Control flow: the test creates a repository, writes `file1`, creates archive 1, writes `file2`, creates archive 2, and expects `/input: 2`. It then writes `file3`, creates archive 3, expects `/input: 5`, deletes `file2`, creates archive 4, and expects `/input: 7`.

State and persistence behavior: mutates files under the archiver input path and persists multiple archives with the same logical match name/history. Repository objects and manifest history are used by analyze to compute deltas.

Dependencies and integration points: covers `analyze` command behavior, archive creation, manifest/archive selection via `-a`, path handling with `pathlib`, and the shared CLI harness.

Risks: expected numeric contributions are tightly tied to chunking/item metadata implementation. Reusing archive name matching can be confusing if archive naming semantics change.

Test signals: validates plain-text analyze output contains expected path contribution counts after additions and deletion.
