<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex -->
# sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex

Purpose: optional hook/helper for extracting media metadata and storing selected fields as git-annex metadata during commits or manual refreshes.

Important configuration and functions: reads `metadata.tool` with default `extract`, `metadata.extract`, `metadata.exiftool`, and `metadata.overwrite`. `addmeta(file, field, value)` converts spaces in field names to underscores and calls `git -c annex.alwayscommit=false annex metadata --set "$field?=$value"` or `=` when overwrite is enabled. `process` runs configured tools against each file, filters output with the configured field regex, parses either `extract`'s `field - value` or exiftool's `field: value`, and calls `addmeta`.

Control flow: exits immediately if no extract fields/tools are configured. Determines diff base as `HEAD` or the empty tree for an initial commit. If arguments are passed, processes those files; otherwise processes staged file names from `git diff-index -z --name-only --cached`, converting NULs to newlines.

State and persistence: mutates git-annex metadata for files and can stage/record annex metadata changes depending on git-annex behavior. No separate state is written.

Dependencies and integration points: Git config, `git annex metadata`, optional `extract` and `exiftool`, `egrep`, `sed`, and pre-commit hook conventions.

Risks: converting NUL-delimited file names to newlines breaks filenames containing newlines. The pipeline uses `eval egrep` with config-derived regex text, which is powerful but risky if untrusted config is present. Tool output parsing is format-specific. Repeated hook runs can be expensive on large files.

Test signals: configure extract/exiftool fields, run against staged and explicit files, test overwrite true/false, initial commit path, missing tools, and filenames with spaces/newlines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex -->
