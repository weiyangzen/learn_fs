# sources/sync-backup/kopia/tools/htmlui_changelog.sh

Purpose: generates a changelog for Kopia HTML UI changes between release points by tracing the `htmluibuild` module hash change in `go.mod` back to commits in the `htmlui` repository.

Control flow/APIs: chooses `start_commit` and `end_commit` from `CI_TAG` or the previous tag. It diffs `go.mod` for `htmluibuild`, extracts old/new htmluibuild hashes, clones `kopia/htmluibuild`, reads automated commit messages to derive old/new htmlui commit hashes, clones `kopia/htmlui`, creates temporary tags on those commits, and runs `$gitchglog --sort=semver --config=... v0.2.0`, appending output to the requested file.

State/persistence: uses fixed temporary directories `/tmp/tmp-htmluibuild` and `/tmp/tmp-htmlui`, deleting any existing directories at those paths. It appends changelog text to the user-provided output file.

Dependencies/integration: requires Git, `realpath`, `grep`, `cut`, an installed `gitchglog` binary exposed as `$gitchglog`, and Kopia changelog config `.chglog/config-htmlui.yml`. Integrated into release-note generation.

Risks/test signals: fixed `/tmp` paths can collide with concurrent runs. Parsing depends on exact `go.mod` diff shape and automated commit-message format. The script uses `set -xe`, so command traces can be noisy. No local tests; release changelog output is the observable signal.
