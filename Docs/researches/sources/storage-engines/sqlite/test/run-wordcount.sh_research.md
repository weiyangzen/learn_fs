# sources/storage-engines/sqlite/test/run-wordcount.sh

## Purpose

`run-wordcount.sh` compares SQLite `wordcount` behavior across rowid and WITHOUT ROWID database variants. It runs the same input through insert, replace, select, query, and delete modes and diffs summarized output.

## Important APIs, Commands, and Files

It requires an input filename and optional extra `wordcount` args. It invokes `./wordcount --timer --summary` with `wcdb1.db` and `wcdb2.db`, using modes `--insert`, `--replace`, `--select`, `--query`, `--delete`, and `--without-rowid`. It uses `cmp -s`, `diff -u`, `mv`, and `rm`.

## Control Flow

The script builds a rowid insert baseline, compares WITHOUT ROWID insert to it, then compares rowid/WITHOUT ROWID replace and select runs to the same baseline. It then creates separate rowid baselines for query and delete and compares WITHOUT ROWID output for each. Differences print `ERROR:` plus a unified diff.

## State and Persistence Behavior

It creates and normally removes `wcdb1.db`, `wcdb2.db`, `wc-out.txt`, and `wc-baseline.txt` in the current directory. The fixed filenames make concurrent runs unsafe.

## Dependencies and Integration Points

It depends on a built `./wordcount` executable and valid input accepted by that program. It integrates with SQLite test/performance tooling as a behavioral equivalence check for rowid versus WITHOUT ROWID storage.

## Risks and Test Signals

If timer output appears in the compared summary, nondeterministic timings can cause false diffs. There is no success output. Cleanup is only at the normal end. The main failure signal is `ERROR:` plus `diff -u`; silence means all comparisons matched.
