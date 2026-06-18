# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots

- Purpose: result reboot detector; it reports whether result summaries indicate VM reboots/preemptions or other restart signals. The file is 20 lines/391 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary; definitions include def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
