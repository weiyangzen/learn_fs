# sources/sync-backup/kopia/tools/scoop-publish.sh

Purpose: publishes or test-publishes Kopia's Scoop manifest by hashing the Windows zip artifact, rendering a JSON template, and pushing to the configured Scoop bucket repository.

Control flow/APIs: positional args are dist directory and version. Production target is `$REPO_OWNER/scoop-bucket`; non-tagged builds use `$REPO_OWNER/scoop-test-builds`. Missing `GITHUB_TOKEN` causes a successful no-op. It computes the Windows amd64 zip SHA-256, clones the target repo, substitutes version/source/hash into `tools/scoop-kopia.json.template`, commits `kopia.json`, and pushes.

State/persistence: creates a temporary clone, writes `kopia.json`, commits/pushes to GitHub, and removes the temp clone on success.

Dependencies/integration: bash, `sha256sum`, `git`, `GITHUB_TOKEN`, `REPO_OWNER`, optional `CI_TAG`, and release artifacts. It is part of Kopia Windows package publication.

Risks/test signals: unquoted variables can break on spaces. Temp cleanup is not protected by traps. The commit message prefixes `v$ver`, so callers must pass a version without duplicate `v` if that matters. Package manager consumers and bucket CI are the downstream test signal.
