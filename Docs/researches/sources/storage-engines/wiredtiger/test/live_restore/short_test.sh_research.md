# sources/storage-engines/wiredtiger/test/live_restore/short_test.sh

Purpose: short live restore smoke suite for build-directory execution.

Important behavior: the script sources `../test/live_restore/helper.sh`, runs a 10-iteration single-collection workload with 1000 operations and INFO-level logging, then runs a small death/recovery pair: `-i 2 -l 2 -d -o 10` followed by `-i 1 -l 2 -r -o 10`.

Control flow and state: commands execute sequentially through `run_test`. The recovery invocation depends on files produced by the preceding death-mode invocation.

Dependencies and integration: same helper and `test_live_restore` binary as long test, but with reduced operation count and collection count for faster validation.

Risks and test signals: useful smoke coverage for live restore startup, CRUD, intentional death, and recovery, but it does not cover high collection counts, per-directory DB mode, or high thread counts from the long suite. Exit 137 is accepted by helper for intentional kills.
