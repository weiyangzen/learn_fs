<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh

Purpose: fetches a pinned Metrix++ source checkout for complexity analysis tasks.

Control flow: clones `https://github.com/metrixplusplus/metrixplusplus` into `metrixplusplus`, enters that directory, and checks out commit `78dc5380de9aaa3d615f8be6c84e90cb2ae0d90b`, then returns to the parent directory.

State and persistence: creates a `metrixplusplus` directory in the current working directory. It does not handle an existing checkout; clone failure exits immediately.

Dependencies and integration: sourced by `coverage-report.sh`, `coverage-report-per-test.sh`, and `cyclomatic-complexity.sh`. The pin exists because the latest code needed by WiredTiger is not available from a release archive and uncontrolled latest changes would destabilize metrics.

Risks and test signals: network dependency on GitHub. The script uses `/bin/sh` but is sourced by Bash wrappers as well. Existing `metrixplusplus` directories cause clone failure. Comment text says the pinned version is latest as of February 28, 2024; changing the pin can alter complexity results and report comparability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh -->
