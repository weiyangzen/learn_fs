<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml

Purpose: Raises macOS file descriptor limits for RocksDB build and test jobs.

Important APIs/types/functions: composite action runs `sudo sysctl -w kern.maxfiles=1048576`, `sudo sysctl -w kern.maxfilesperproc=1048576`, and `sudo launchctl limit maxfiles 1048576`.

Control flow: a single bash step applies system-level settings before build/test commands run.

State and persistence behavior: changes runner kernel/session limits for the lifetime of the GitHub-hosted runner job; no repository state is modified.

Dependencies and integration points: used by macOS PR jobs and Java/macOS jobs before make or ctest. Depends on sudo access on macOS runners.

Risks: hosted runner policy changes could reject these sysctl/launchctl calls. Individual shells still often call `ulimit` afterward, so this action alone may not guarantee the soft limit.

Test signals: macOS logs should show successful sysctl/launchctl commands and later RocksDB tests should avoid EMFILE failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml -->
