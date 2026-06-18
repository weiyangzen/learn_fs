# File Research: sources/virtualization/guestfs-tools/bash/test-complete-in-script.sh

## Scope

Test ensuring each bash completion script or symlink contains a matching `complete` command.

## Behavior

- Requires the `commands` environment variable, normally supplied by `make check`.
- For each command, verifies the script/symlink exists and contains a `complete` rule ending with that command name.
- Fails with diagnostic messages for missing files or mismatched completion declarations.

## Dependencies And Risks

- Depends on generated symlinks being present in the build directory.
- Uses grep against shell completion text, so format changes in completion scripts must preserve recognizable `complete ... command` lines.
