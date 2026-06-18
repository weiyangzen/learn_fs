# sources/sync-backup/kopia/.github/workflows/compat-test.yml

Purpose: compatibility test workflow for master, tags, and PRs.

Important APIs/types/functions: triggers on master push, version tags, and PRs; checkout, setup-go from `go.mod`, `make compat-tests`, and log upload.

Control flow: runs compatibility test make target and uploads logs regardless of outcome.

State and persistence: CI artifacts/logs only.

Dependencies and integration points: depends on repository Makefile compatibility target.

Risks: broad trigger on tags means release tags depend on this target stability.

Test signals: direct workflow result.
