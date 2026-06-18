# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.fish

## Purpose
Fish shell completion fixture for `git-lfs`, generated from Cobra completion support and used as the expected output by the completion integration tests. It translates Fish command-line state into a `git-lfs __completeNoDesc` request, then adapts the completion directive protocol to Fish's `complete` command.

## Important APIs, Functions, and Control Flow
The main helpers are `__git_lfs_debug`, `__git_lfs_perform_completion`, `__git_lfs_perform_completion_once`, `__git_lfs_clear_perform_completion_once_result`, `__git_lfs_requires_order_preservation`, and `__git_lfs_prepare_completions`. Completion starts from `commandline -opc` and `commandline -ct`, disables active help with `GIT_LFS_ACTIVE_HELP=0`, evaluates the request, strips trailing blank lines, separates candidates from the final `:<directive>` line, and prefixes flag-value completions when the current token matches `-.*=`.

## State, Persistence, and Dependencies
The script uses global Fish variables `__git_lfs_perform_completion_once_result` and `__git_lfs_comp_results` to cache one completion invocation per completion cycle. It depends on Fish builtins (`commandline`, `string`, `math`, `complete`) and on the installed `git-lfs` binary. Debug output appends to `BASH_COMP_DEBUG_FILE` when set.

## Integration Points, Risks, and Test Signals
It registers completions for `git-lfs`, first clearing any prior completions after triggering lazy completion loading. Directive bits handle error, no-space, no-file, extension filtering, directory filtering, and keep-order behavior; Fish lacks direct support for some filtering modes, so the script falls back to file completion. Risks cluster around `eval` quoting, directive parsing, and cache invalidation. `t-completion.sh` compares `git lfs completion fish` against this fixture byte-for-byte.
