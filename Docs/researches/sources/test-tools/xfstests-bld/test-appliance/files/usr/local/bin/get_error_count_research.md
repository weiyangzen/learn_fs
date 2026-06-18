# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count

- Purpose: xUnit error counter; it returns aggregate error/failure counts from a JUnit XML document for runner exit decisions. The file is 26 lines/594 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
