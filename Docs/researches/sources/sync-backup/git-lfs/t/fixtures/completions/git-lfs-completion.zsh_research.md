# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.zsh

## Purpose
Zsh completion fixture for `git-lfs`, also serving as a golden output for `git lfs completion zsh`. It adapts Cobra's completion protocol to zsh's completion system, including descriptions, active help, file filters, directory filters, no-space behavior, and order preservation.

## Important APIs, Functions, and Control Flow
The file defines `__git-lfs_debug` and `_git-lfs`, then registers `_git-lfs` for `git-lfs` with `compdef`. `_git-lfs` truncates `words` to `CURRENT`, computes a `git-lfs __completeNoDesc ...` request, appends an empty argument when the last parameter is complete, evaluates the request, extracts the trailing directive, and processes each completion line. Completion descriptions are converted from tab-separated Cobra output into zsh `_describe` colon syntax, with colons escaped.

## State, Persistence, and Dependencies
State is local to the completion invocation except optional debug logging through `BASH_COMP_DEBUG_FILE`. The script depends on zsh arrays, `compadd`, `_describe`, `_arguments`, and `_files`. The directive constants mirror Cobra shell completion directive bits.

## Integration Points, Risks, and Test Signals
It integrates with `git-lfs` by invoking `git-${words[1]#*git-}`, supporting invocation through aliases such as `git lfs`. Active help lines prefixed with `_activeHelp_ ` are displayed with zsh explanation groups. Risks include `eval` quoting, shell-specific array slicing, and fallback behavior when `_describe` finds no candidates. `t-completion.sh` validates this fixture by exact comparison with generated zsh completion output.
