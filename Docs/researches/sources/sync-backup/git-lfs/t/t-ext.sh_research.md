# sources/sync-backup/git-lfs/t/t-ext.sh

## Purpose

Tests `git lfs ext` and `git lfs ext list` reporting for configured LFS pointer extensions. It confirms extension names, clean/smudge commands, priority values, filtering by extension names, and default listing behavior.

## Important APIs, control flow, and dependencies

The test initializes one repository, configures `lfs.extension.foo`, `bar`, and `baz` clean/smudge/priority entries, builds expected output strings, and compares command output for `git lfs ext list foo`, `bar`, `baz`, multiple named args, no args, and `git lfs ext`.

## State, dependencies, integration points, risks, and test signals

State is Git config only. Integration points are extension config parsing, stable ordering, command alias behavior, and output formatting. Risks include sorting by name rather than priority, omitting fields, or diverging `ext` from `ext list`. Signals are exact string equality for every command form.
