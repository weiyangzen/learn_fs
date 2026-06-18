# sources/test-tools/lcov/scripts/gitdiff

Purpose: extracts a unified diff between two git revisions, optionally filtered by include/exclude regexps, and optionally emits placeholder entries for unchanged files so downstream diffcov/genhtml code can disambiguate basenames.

Important APIs: command usage accepts optional `[dir] base_SHA current_SHA` plus `--repo`, `--prefix`, `--include`, `--exclude`, `--no-unchanged`, `-b/--blank`, and `--verbose`.

Control flow and state: include/exclude options are comma-expanded. The script runs `git diff` in the realpath of `--repo`, rewrites `a/` and `b/` path prefixes to the configured prefix, tracks files seen in diff headers, and prints only included file hunks. Unless `--no-unchanged` is set, it then runs `git ls-tree -r --name-only` for the current SHA and emits synthetic `diff --git` plus `===` markers for included files not in the diff.

Dependencies and integration: uses git CLI, `Getopt::Long`, and `Cwd::realpath`. It is a diff-file generator for lcov/genhtml differential coverage.

Risks and test signals: include/exclude regexps run against git-style paths after partial prefix manipulation; path normalization can produce absolute repo-prefixed synthetic paths unlike raw diff headers. Shell command interpolation is unquoted. Tests should cover changed, deleted, added, unchanged, whitespace-ignored, include/exclude, and prefix modes.
