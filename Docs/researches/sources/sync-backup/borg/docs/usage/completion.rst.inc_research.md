# sources/sync-backup/borg/docs/usage/completion.rst.inc

Purpose: generated reference for `borg completion`, which prints a shell completion script.

Important APIs and control flow: command takes a required `SHELL` choice from the completion generator's supported shell set. It emits completion code to stdout.

State and persistence: no repository mutation. Users may persist output into shell-specific completion locations outside Borg.

Dependencies and integration points: generated completions may call Borg dynamically for archive IDs and repository information, so they integrate with repository location and passphrase environment variables.

Risks: the visible `%(choices)s` placeholder suggests a generation bug or unresolved argparse interpolation in this include. Dynamic completion can hang or prompt if repository/passphrase access is not non-interactive.

Test signals: generated docs should render concrete shell choices; completion scripts should parse in supported shells and avoid interactive prompts when `BORG_REPO`/passphrase variables are set.
