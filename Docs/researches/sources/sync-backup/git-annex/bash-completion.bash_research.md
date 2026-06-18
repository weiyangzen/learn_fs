<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/bash-completion.bash -->
# sources/sync-backup/git-annex/bash-completion.bash

Purpose: Bash completion adapter that delegates completion generation to `git-annex` itself, avoiding a static list of commands or options.

Important functions: `_git-annex` builds `CMDLINE` with `--bash-completion-index $COMP_CWORD` and one `--bash-completion-word` per `COMP_WORDS` entry, then sets `COMPREPLY` from `git-annex` output. `_git_annex` adapts Git's `git annex` completion callback to the standalone `git-annex` command by replacing the first `git`/`annex` pair with a synthetic `git-annex` completion word and reducing the completion index by one.

Control flow: direct `git-annex` completion is registered via `complete -o bashdefault -o default -o filenames -F _git-annex git-annex`. Git's own completion can call `_git_annex` for `git annex`; that path preserves filename completion behavior using `compopt -o filenames +o nospace` with a compatibility fallback.

State and persistence: no durable state; it depends on Bash's `COMP_WORDS`, `COMP_CWORD`, `COMPREPLY`, and local arrays.

Dependencies and integration points: requires Bash completion semantics and a runnable `git-annex` in `PATH`. It integrates with the internal `git-annex --bash-completion-*` protocol and optionally with `git-completion.bash`.

Risks: array expansions are unquoted, so arguments containing whitespace can be split before being passed to `git-annex`. Completion behavior depends on `git-annex` being fast enough for interactive shell use. `compopt` is Bash-specific and guarded only by a fallback command chain.

Test signals: source the script in Bash, verify `git-annex <TAB>` and `git annex <TAB>` completions, include filenames with spaces, and check behavior when `git-annex` is missing or slow.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/bash-completion.bash -->
