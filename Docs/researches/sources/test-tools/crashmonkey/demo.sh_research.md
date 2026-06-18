# sources/test-tools/crashmonkey/demo.sh

Purpose: end-to-end demo driver for generating ACE workloads, compiling them, running XFSMonkey on a selected filesystem, and printing a timing/bug summary.

Important APIs/types/functions: argument `FS`, ACE invocation `python ace.py -l 1 -n False -d True`, `make gentests`, `xfsMonkey.py`, summary files `bugs`, `stat`, `missing`, `others`, and directories `code/tests/seq1_demo`, `generated_workloads`, `build/tests/generated_workloads`, `diff_results`.

Control flow: validates one filesystem argument, removes old generated workload dir, runs ACE, clears/copies generated `j-lang*.cpp`, compiles generated tests, initializes counters, removes old reports, runs `xfsMonkey.py`, then computes generation/compile/test durations and prints counts.

State/persistence behavior: deletes and recreates workload/report directories, writes counter files, writes `out_compile`, and creates logs/diffs through XFSMonkey. Dependencies/integration: requires ACE, make targets, root-capable XFSMonkey environment, and `bc`.

Risks/test signals: destructive cleanup is broad, paths are relative to repository root, summary says `diff-results` while variable is `diff_results`, and failures in generation/compile are not explicitly checked before running tests.
