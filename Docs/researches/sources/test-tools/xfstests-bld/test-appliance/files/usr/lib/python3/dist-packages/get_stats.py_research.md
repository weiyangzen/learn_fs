# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py

- Purpose: JUnit statistics extractor; it reads result directories and emits compact stats used by diff/merge/check helper scripts. The file is 69 lines/2317 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary, junitparser; definitions include def get_stats_from_dir, def write_stats, def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
