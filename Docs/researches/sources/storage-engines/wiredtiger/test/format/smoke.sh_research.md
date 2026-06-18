# sources/storage-engines/wiredtiger/test/format/smoke.sh

Purpose: make-check smoke wrapper for the format binary.

Important commands and parameters: builds a common `args` string with `-c .`, compression/logging compression off, `cache.minimum=40`, `runs.rows=100000`, table source, three tables, six threads, one-minute timer, and transaction timestamps enabled; runs `$TEST_WRAPPER ./t ... runs.type=row` and then `runs.type=var`.

Control flow: `set -e` fails on any command error. The script performs two short format runs, one row-store and one variable column-store.

State and persistence: creates whatever `./t` creates in its default `RUNDIR` unless wrapper/config overrides. It does not clean by itself.

Dependencies and integration: used by build/test harness, depends on `TEST_WRAPPER`, local format binary `./t`, and generated format configuration parser.

Risks and test signals: because `set -e` is active, non-zero format exit fails smoke. It provides quick coverage for timestamped multi-table row and var workloads but not the full option surface.
