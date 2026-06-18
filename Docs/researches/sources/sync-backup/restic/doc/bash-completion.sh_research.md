# sources/sync-backup/restic/doc/bash-completion.sh

## Purpose

This generated Bash completion script wires restic command, flag, and dynamic completion behavior into Bash's `complete` system. It combines static Cobra-generated command/flag tables with runtime calls to `restic __completeNoDesc` for commands that expose Go-side completion functions.

## Important APIs, Types, and Functions

- `__restic_debug` appends debug messages to `BASH_COMP_DEBUG_FILE` when set.
- `__restic_init_completion` provides a minimal fallback for systems without Bash completion's `_init_completion`.
- `__restic_index_of_word` and `__restic_contains_word` are utility search helpers for arrays.
- `__restic_handle_go_custom_completion` invokes `RESTIC_ACTIVE_HELP=0 <cmd> __completeNoDesc ...`, parses Cobra shell completion directives, and populates `COMPREPLY`.
- `__restic_handle_reply` decides whether to complete flags, flag values, subcommands, nouns, dynamic Go completions, or fallback custom functions.
- `__restic_handle_filename_extension_flag`, `__restic_handle_subdirs_in_dir_flag`, `__restic_handle_flag`, `__restic_handle_noun`, `__restic_handle_command`, and `__restic_handle_word` implement the parser/walker for the current command line.
- `_restic_<command>` functions, such as `_restic_backup`, `_restic_forget`, `_restic_generate`, `_restic_restore`, and many others, populate command-local arrays: `commands`, `flags`, `two_word_flags`, `local_nonpersistent_flags`, `flags_with_completion`, `flags_completion`, `must_have_one_flag`, `must_have_one_noun`, and aliases.
- `_restic_root_command` declares top-level subcommands and global persistent flags.
- `__start_restic` initializes parser state and calls `__restic_handle_word`.
- Final registration calls `complete -o default -F __start_restic restic` or adds `-o nospace` when `compopt` is unavailable.

## Control Flow

When Bash requests completion for `restic`, `__start_restic` obtains `cur`, `prev`, `words`, and `cword`, initializes state arrays, and recursively processes each word. Command words dispatch to `_restic_root_command` or a command-specific `_restic_*` function. Flags update required flag/noun state, may consume the following value for two-word flags, and suppress subcommands when a local nonpersistent flag has been seen. Once the parser reaches the current word, `__restic_handle_reply` builds completion candidates.

For dynamic completions, the script calls the running restic binary's hidden Cobra completion endpoint. It parses the trailing directive bitmask for error, no-space, no-file-completion, file-extension filtering, and directory filtering. It then either uses `_filedir`, directory-only completion, or `compgen` to populate `COMPREPLY`.

## State and Persistence Behavior

The script stores only shell-local and completion-session state. It may temporarily set associative arrays `flaghash` and `aliashash` when supported by Bash. It does not persist files except optional debug logging to the user-selected `BASH_COMP_DEBUG_FILE`.

## Dependencies and Integration Points

It depends on Bash completion primitives (`complete`, `compopt`, `_get_comp_words_by_ref`, `_filedir`) with fallbacks for older macOS/Homebrew environments. Its runtime integration depends on the installed `restic` executable supporting Cobra hidden completion commands. The static command/flag tables must be regenerated when CLI commands or flags change, normally via restic's `generate` command and release tooling.

## Risks and Edge Cases

- Generated static flag tables can drift from command code if not regenerated.
- Dynamic completion uses `eval` to run the constructed completion command, matching Cobra's generated pattern but requiring careful quoting of command words.
- Bash 3 lacks associative arrays; the script degrades alias/flag hash behavior for compatibility.
- Active Help is disabled for Bash completion v1.
- Completion directive parsing assumes the final colon-suffixed directive format emitted by Cobra.
- Missing `_filedir` or `_get_comp_words_by_ref` on nonstandard environments can reduce completion quality.

## Test Signals

Manual shell completion, generated completion comparison, and release `generateFiles` flows are the primary signals. The script should also be indirectly checked by invoking `restic generate --bash-completion` and comparing the committed output.
