# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.bash

Purpose: bash completion fixture for Git LFS, generated in Cobra-style completion protocol format and used by tests.

Important functions: `__git-lfs_debug`, `__git-lfs_init_completion`, `__git-lfs_get_completion_results`, `__git-lfs_process_completion_results`, `__git-lfs_extract_activeHelp`, `__git-lfs_handle_completion_types`, `__git-lfs_handle_standard_completion_case`, `__git-lfs_handle_special_char`, `__git-lfs_format_comp_descriptions`, `__start_git-lfs`, and `_git_lfs`.

Control flow: completion setup initializes `cur/prev/words/cword`, rewrites `git lfs` invocations to `git-lfs`, calls `git-lfs __completeNoDesc` via eval, separates output from the trailing directive, applies directive bits for nospace, no file completion, file-extension filtering, directory filtering, and keep-order, then builds `COMPREPLY` with description formatting and active help rendering.

State/persistence behavior: no persistence except optional debug appends to `BASH_COMP_DEBUG_FILE`. It mutates shell variables and completion options.

Dependencies/integration: depends on bash-completion helpers `_init_completion`, `_get_comp_words_by_ref`, `_filedir`, `compopt`, and the Git LFS binary's completion protocol.

Risks: uses `eval` to invoke the completion request, so quoting of words is sensitive. Bash version differences affect `nosort`, prompt rendering, and `compopt` behavior.

Test signals: shell completion tests can assert `COMPREPLY`, directive behavior, active help, special `:`/`=` handling, and registration for `git-lfs`.
