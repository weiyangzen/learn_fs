# Research: sources/sync-backup/syncthing/script/codecov-upload.sh

## sources/sync-backup/syncthing/script/codecov-upload.sh

Purpose: vendored Codecov Bash uploader that detects CI metadata, discovers coverage reports, builds an upload payload, and sends it to Codecov.

Important APIs/functions: command-line parser for many short options; `show_help`, `say`, `urlencode`, `swiftcov`, `parse_yaml`, `cleanup`; feature toggles for gcov, coverage.py, search, network, Xcode, S3, report fixing, HTML/YAML inclusion, and direct upload.

Control flow: initializes defaults from environment, parses flags, detects tools, detects CI provider from environment, resolves branch/commit/slug/token/url from overrides/env/yaml/VCS, optionally runs Xcode/gcov/coverage.py processing, searches for coverage reports while pruning dependency/cache paths, builds a network file list, appends reports and adjustments to a temp upload file, optionally dumps/saves it, gzips it, then uploads via Codecov v4 S3 pre-signed flow or v2 fallback.

State and persistence: creates temp upload and adjustments files, optional saved payload, optional deletion of coverage files with `-c`. Network state includes Codecov and optional AWS storage targets.

Dependencies and integration: Bash, curl, git/hg, find, awk/sed, gzip, gcov, coverage.py, xcrun/plutil for Apple coverage. Risks include shell quoting/eval complexity, credentials in query construction, many CI-provider branches, temp cleanup only on selected signals, and reliance on deprecated Codecov bash behavior. Test signal is CI coverage upload success/failure logs.
