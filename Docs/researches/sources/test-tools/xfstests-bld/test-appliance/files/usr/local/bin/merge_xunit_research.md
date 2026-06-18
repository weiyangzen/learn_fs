# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit

- Purpose: xUnit merge utility; it merges one JUnit XML file into another while preserving suite/test statistics. The file is 33 lines/865 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
