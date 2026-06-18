# sources/sync-backup/kopia/tools/homebrew-publish.sh

Purpose: publishes or test-publishes Kopia Homebrew formula updates by computing release artifact hashes, rendering a Ruby formula template, and pushing it to the configured Homebrew tap repository.

Control flow/APIs: positional args are distribution directory and version. The script selects production repos when `CI_TAG` is present and test-build repos otherwise. It exits successfully without publishing when `GITHUB_TOKEN` is missing. It computes SHA-256 hashes for macOS and Linux tarballs, clones `$REPO_OWNER/homebrew-kopia` or `$REPO_OWNER/homebrew-test-builds`, applies `sed` substitutions to `tools/kopia-homebrew.rs.template`, commits, and pushes.

State/persistence: creates a temporary clone with `mktemp -d`, writes `kopia.rb`, commits to a remote GitHub repository, and removes the temporary directory at the end.

Dependencies/integration: requires bash, `sha256sum`, `git`, network access, `GITHUB_TOKEN`, `REPO_OWNER`, optional `CI_TAG`, release artifacts, and the Homebrew template. It is part of Kopia release automation.

Risks/test signals: most variables and paths are unquoted, so paths containing whitespace can break. Failures before `rm -rf` leave temp clones. The token is embedded in the clone URL, so CI log redaction must be relied on. There is no dedicated test; release CI and successful tap updates are the signal.
