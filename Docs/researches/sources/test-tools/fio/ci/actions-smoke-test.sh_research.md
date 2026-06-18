## sources/test-tools/fio/ci/actions-smoke-test.sh

Purpose: minimal CI smoke-test entrypoint.

Important flow: `main()` returns immediately for Android builds, prints a status line, and runs `make test` for all other targets. It uses `set -eu` to fail on command errors and unset variables.

State and persistence: no private state; generated state is whatever `make test` produces in the build tree.

Dependencies and integration: depends on the Makefile produced by `configure`, a completed build, and platform dependencies from `actions-install.sh`. Android is skipped because the build is cross-compiled or otherwise not runnable in this lane.

Risks and test signals: because it is intentionally small, it only catches basic build/test failures. `CI_TARGET_BUILD` must be present under `set -u`; the workflow must set it before invoking the script.
