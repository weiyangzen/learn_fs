<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml

Purpose: Prepares an upstream remote and safe repository ownership for format-compatibility and source-check jobs.

Important APIs/types/functions: runs `chown $(whoami) . || true`, `git remote add upstream https://github.com/facebook/rocksdb.git`, `git fetch upstream`, and diagnostic `git status && git remote -v && env -i git branch`.

Control flow: ownership fix, remote setup, fetch, then diagnostics.

State and persistence behavior: mutates local git config/remotes and fetches upstream refs into the CI checkout.

Dependencies and integration points: used by `check-format-and-targets` and `nightly` format-compatible jobs that need full upstream history or branch behavior under `env -i`.

Risks: action name is incorrectly `build-folly`, which can confuse logs. `git remote add upstream` fails if remote already exists; no `|| true` is present there. Network fetch from GitHub is required.

Test signals: successful upstream fetch and `check_format_compatible.sh` running against expected history.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml -->
