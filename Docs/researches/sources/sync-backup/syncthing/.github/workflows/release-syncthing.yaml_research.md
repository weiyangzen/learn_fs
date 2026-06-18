# sources/sync-backup/syncthing/.github/workflows/release-syncthing.yaml

Purpose: release-tag automation for pushes to `release` and `release-rc*` branches.

Important APIs/types/functions: job `create-release-tag` checks out full history with `ACTIONS_GITHUB_TOKEN`, sets up stable Go, runs `script/next-version.go` with or without `--pre`, determines previous stable tag, generates notes using `script/relnotes.go`, creates an annotated tag, pushes it, then dispatches `build-syncthing.yaml` for the new tag.

Control flow: release branch chooses stable next version; release-rc branches choose prerelease version. Notes are generated before tag creation. The build workflow is explicitly triggered on `refs/tags/$NEXT`.

State and persistence behavior: creates and pushes Git tags and triggers downstream release artifact state.

Dependencies/integration: depends on release scripts, Git tag history, GitHub token permissions, and `benc-uk/workflow-dispatch`.

Risks/test signals: incorrect version calculation or notes can create bad immutable tags. Signal is an annotated tag with expected notes and a downstream build workflow run for that tag.
