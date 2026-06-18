# sources/sync-backup/git-lfs/t/t-install-custom-hooks-path-unsupported.sh

## Purpose

Version-gated test for Git versions without `core.hooksPath` support. It confirms `git lfs install` falls back to `.git/hooks` instead of writing into a configured custom hook path.

## Important APIs, control flow, and dependencies

The script uses `ensure_git_version_isnt $VERSION_HIGHER "2.9.0"`, initializes a repo, creates `custom_hooks_dir`, sets `core.hooksPath`, runs `git lfs install`, and checks hook file locations.

## State, dependencies, integration points, risks, and test signals

State is the repository config and hook directories. Integration points are Git-version feature detection and hook installation path selection. Risks include blindly honoring unsupported `core.hooksPath` or failing to install hooks at all. Signals are `Updated Git hooks`, absence of `custom_hooks_dir/pre-push`, and presence of `.git/hooks/pre-push`.
