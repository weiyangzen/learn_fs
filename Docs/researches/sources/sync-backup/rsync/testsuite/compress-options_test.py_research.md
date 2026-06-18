# sources/sync-backup/rsync/testsuite/compress-options_test.py

Purpose: breadth coverage of compression and checksum option negotiation at depth without changing transfer results.

Important APIs/types/functions: JSON `-VV` parsing for `compress_list` and `checksum_list`, `fresh`, `verify`, `run_rsync`, `--debug=NSTR`, regex checks, and `assert_same`.

Control flow: for every advertised compressor except `none`, build a fresh depth-3 data tree, run `-az --compress-choice=ALGO --debug=NSTR`, assert debug output selected that compressor, and verify bytes. Then test `--compress-level=9`, `--skip-compress=gz`, every checksum algorithm with `-c --checksum-choice=ALGO`, and `--checksum-seed=12345`.

State and persistence behavior: repeatedly recreates source and destination, and injects a pseudo-gzip file for skip-compress. Destination content must remain byte-identical.

Dependencies and integration points: rsync algorithm negotiation, debug output contracts, compression/checksum lists from `-VV`, and data-tree helpers.

Risks and test signals: depends on debug text format. Failures mean requested algorithms were not negotiated or data was corrupted.
