# sources/test-tools/xfstests-bld/selftests/util/check_results.py

- Purpose: selftest result checker; it parses JUnit XML and compares observed test counts, failures, skips, and errors against expected assertions. The file is 38 lines/1754 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/check_results.py`.
- Important APIs/types/functions: Python imports sys, argparse, junitparser, get_stats; definitions include top-level CLI logic.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
