# sources/sync-backup/git-lfs/t/t-install.sh

## Purpose

Broad coverage for `git lfs install`: idempotence, upgrade behavior, repo hook generation/update, outside-repo behavior, `--skip-smudge`, `--local`, `--file`, permission failures, scope conflicts, inaccessible `.git/lfs`, `--skip-repo`, and multiple global config values.

## Important APIs, control flow, and dependencies

The tests inspect and set `filter.lfs.clean`, `smudge`, and `process` in global/local/file scopes; run `git lfs install` with `--skip-repo`, `--force`, `--skip-smudge`, `--local`, and `--file`; compare expected hook script bodies for `pre-push`, `post-checkout`, `post-commit`, and `post-merge`; create mirror/bare repos; simulate permission failures by chmodding `.git`; and verify conflicting scope options.

## State, dependencies, integration points, risks, and test signals

State includes Git config scopes, hook files, repository/bare hooks directories, permissions, and generated output. Integration points are Git config writes, hook updater, skip-smudge filter-process settings, non-repository install semantics, and error propagation from `git config`. Risks include using `--replace-all` unnecessarily, clobbering unknown hooks without force, modifying wrong config scope, failing in bare repos, and bad exit codes. Signals are exact config values, hook body equality, output string equality, grep for permission/config errors, and hook presence/absence checks.
