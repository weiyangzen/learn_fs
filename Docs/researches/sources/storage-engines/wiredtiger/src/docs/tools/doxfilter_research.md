# sources/storage-engines/wiredtiger/src/docs/tools/doxfilter

## Purpose
Shell wrapper for the C/comment Doxygen filter.

## APIs and control flow
The script determines its directory with `dirname $0` and executes `python $tooldir/doxfilter.py "$@"`. It preserves all arguments for Doxygen's input-filter invocation.

## State, dependencies, integration, risks
The wrapper has no state. It depends on `/bin/sh`, `python` on `PATH`, and `doxfilter.py` in the same directory. It integrates with Doxygen `INPUT_FILTER` configuration where a stable executable script path is more convenient than embedding a Python script path. Risks are Python version ambiguity and paths containing unusual shell characters. Test signals are executable permissions and successful filtered output for a sample documented C source.
