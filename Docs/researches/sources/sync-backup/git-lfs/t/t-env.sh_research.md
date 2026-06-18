# sources/sync-backup/git-lfs/t/t-env.sh

## Purpose

Provides exact-output contract coverage for `git lfs env`. It validates repository discovery, remote endpoint rendering, LFS storage paths, transfer lists, default configuration, environment-variable reporting, bare repository handling, SSH endpoint conversion, Unicode paths, locale behavior outside a repo, and duplicate URL alias warnings.

## Important APIs, control flow, and dependencies

The script builds expected multiline output using `git lfs version`, `git version`, `canonical_path`, `native_path`, `setup_expected_concurrent_transfers`, current `GIT_*` environment variables, and expected filter config lines. It creates repos with no remote, one or more remotes, `lfs.url`, `remote.<name>.lfsurl`, `.lfsconfig`, explicit `GIT_DIR`/`GIT_WORK_TREE`, bare repos, SSH remotes, transfer config, and URL `insteadOf` aliases. Most tests compare `git lfs env | grep -v "^GIT_EXEC_PATH="` with `contains_same_elements`.

## State, dependencies, integration points, risks, and test signals

State includes `.git/config`, `.lfsconfig`, `.gitconfig`, global environment, bare/non-bare repo layout, `.git/lfs` paths, remote names, and URL rewrite config. Integration points are config precedence, endpoint discovery, path canonicalization, Git environment handling, transfer adapter registration, SSH URL derivation, and warning emission. Risks include unstable output ordering, leaking unrelated `TEST_GIT_*` variables, incorrect local path when run from `.git` or subdirectories, mishandling invalid relative work trees, broken Unicode/locale handling, and missing duplicate-alias warnings. Signals are full expected/actual output equality by element and targeted greps for endpoint, SSH, transfer, and warning lines.
