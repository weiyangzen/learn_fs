<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go

## Purpose

`genautocomplete_zsh.go` implements `rclone completion zsh`.

## Important APIs, Types, and Functions

`init` attaches `zshCommandDefinition`. The command defaults to `/usr/share/zsh/vendor-completions/_rclone`, writes stdout for `-` with `cmd.Root.GenZshCompletion`, or creates the target file and generates zsh completion into it.

## Control Flow

Argument validation allows zero or one arg. File creation happens manually with `os.Create`, then a deferred close ignores close errors.

## State and Persistence Behavior

It creates or truncates a local zsh completion file or writes to stdout.

## Dependencies and Integration Points

It integrates with Cobra zsh completion generation, OS file APIs, and the root command tree.

## Risks and Test Signals

Risks include root-only default path, ignored close errors, truncating existing files before generation succeeds, and shell generator drift. Tests should cover stdout, custom files, generation errors, and close/write failures where practical.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go -->
