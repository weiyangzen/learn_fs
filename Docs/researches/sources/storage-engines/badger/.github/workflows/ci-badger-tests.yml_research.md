# sources/storage-engines/badger/.github/workflows/ci-badger-tests.yml

Purpose: core Badger CI for cross-compilation and test execution.

Important flow: it runs manually and on pull requests to `main` or `release/v*`, ignoring docs/images/contrib. The `cross-compile` matrix builds `./...` for Linux, Darwin, Windows, AIX, and Plan 9 combinations. The `badger-tests` job installs dependencies through `make dependency` and runs `make test`.

State and persistence: no release artifacts are produced; outputs are CI logs and test status. Dependencies include `actions/setup-go`, Go module metadata, system package installation, and repository test scripts. Risks: cross-compile catches build tags/import problems but not runtime behavior; `make dependency` uses sudo apt and can dominate runtime; `make test` delegates to `test.sh`, which is outside this item. Test signals are cross-compile success, full Badger test pass, and path-ignore correctness.
