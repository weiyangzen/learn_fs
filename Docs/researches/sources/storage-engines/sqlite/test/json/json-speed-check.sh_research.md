# sources/storage-engines/sqlite/test/json/json-speed-check.sh

## Purpose

`json-speed-check.sh` is a day-to-day SQLite JSON/JSONB performance helper. It builds a local `jsonshell` from `shell.c` and `sqlite3.c`, runs a JSON workload under Valgrind Cachegrind, annotates the profile, and optionally opens a Fossil diff against a baseline.

## Important APIs, Commands, and Variables

The first argument is `NAME`, used for `summary-$NAME.txt` and `$TYPE-$NAME.txt`. Options include `--nodiff`, `--lean`, `--clang`, `--gcc7`, `--jsonb`, and arbitrary compiler flags. Key commands are `$CC`, `valgrind --tool=cachegrind`, `cg_anno.tcl`, `tee`, `sed`, `ls`, and `fossil xdiff --tk`.

## Control Flow

The script validates `NAME`, parses flags, appends lean compile options if requested, switches `TYPE=jsonb` for `--jsonb`, logs build metadata, removes prior Cachegrind output and `jsonshell`, compiles the shell, runs a query file from the script directory under Cachegrind, writes annotated output, appends normalized summary text, and optionally diffs against `$TYPE-$BASELINE.txt`.

## State and Persistence Behavior

It creates or overwrites `jsonshell`, `cachegrind.out.*`, `summary-$NAME.txt`, and `$TYPE-$NAME.txt`. It reads workload DB/query files such as JSON/JSONB 100MB databases and `$TYPE-q1.txt`. It does not clean final summaries.

## Dependencies and Integration Points

It assumes an SQLite amalgamation directory, Valgrind, `cg_anno.tcl`, Fossil/Tk for diffs, and prebuilt JSON workload databases. It integrates with SQLite performance monitoring by producing comparable Cachegrind annotation files.

## Risks and Test Signals

The command echoes `$DB` but the Valgrind invocation hardcodes `json100mb_b.db`, which can break JSONB or renamed-DB runs. Several variables are unused. Missing tooling or workload files fail at runtime. Signals are successful shell build, non-empty summary/profile files, and meaningful Fossil diffs versus baseline.
