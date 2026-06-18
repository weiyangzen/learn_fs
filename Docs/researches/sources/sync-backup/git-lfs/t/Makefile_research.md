# sources/sync-backup/git-lfs/t/Makefile

Purpose: builds integration-test helper binaries and runs shell test suites.

Important targets/variables: `TEST_CMDS`, `TEST_SRCS`, `TEST_API_SRCS`, `test-commands`, `test`, per-test shell targets, `clean`, pattern rule `../bin/%$X : cmd/%.go`, and `../bin/git-lfs-test-server-api$X`.

Control flow: detects Windows executable suffix, lists all Go helper tools, builds them with `go build`, runs `testenv.sh` setup, executes `prove` over `t-*.sh`, then shuts down. Per-test targets run one script with verbose prove.

State/persistence behavior: creates binaries under `../bin`, removes `remote` and test count/lock files, and uses `GOTOOLCHAIN=local` to prevent automatic Go downloads.

Dependencies/integration: called by `script/cibuild` and local integration-test workflows.

Risks: helper list must stay in sync with `t/cmd`. Cleanup is limited to known test state and binaries.

Test signals: successful target proves helper compilation and shell integration tests pass.
