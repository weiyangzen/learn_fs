# sources/sync-backup/restic/doc/fish-completion.fish

## Purpose

This generated Fish shell completion script integrates restic with Fish's `complete` system. It delegates actual command-specific completion generation to restic's Cobra completion endpoint and adapts Cobra directives to Fish behavior.

## Important APIs, Types, and Functions

- `__restic_debug` writes debug output to `BASH_COMP_DEBUG_FILE` when set.
- `__restic_perform_completion` reads the current Fish commandline, disables Active Help with `RESTIC_ACTIVE_HELP=0`, calls `<program> __complete`, strips trailing empty lines, applies flag `--x=` prefixes, prints completions, and prints the directive line.
- `__restic_perform_completion_once` caches the completion result in the global variable `__restic_perform_completion_once_result` so multiple Fish `complete` invocations in one completion cycle do not rerun restic.
- `__restic_clear_perform_completion_once_result` clears that cache after completion.
- `__restic_requires_order_preservation` checks the Cobra `KeepOrder` directive bit and controls whether Fish's `-k` option is used.
- `__restic_prepare_completions` parses directive bits, stores candidate completions in `__restic_comp_results`, handles no-space/no-file-completion semantics as far as Fish allows, and decides whether to fall back to file completion.
- Final `complete` calls clear old completions, install cache clearing, and register ordered or normal completion candidates for `restic`.

## Control Flow

When completion is requested, Fish evaluates the registered conditions. The script calls `__restic_perform_completion_once`, which invokes restic at most once for the current completion attempt. `__restic_prepare_completions` parses the last line directive, filters completions by the current token prefix when needed, handles unsupported file-extension/directory filters by requesting normal file completion, and stores candidates for the `complete -a` argument. `__restic_requires_order_preservation` may run against the same cached result to decide whether to use `complete -k`.

## State and Persistence Behavior

The script uses global Fish variables as short-lived completion caches and erases them after use. It has no persistent state except optional debug logging. It proactively triggers existing completions with `complete --do-complete "restic "` when `restic` is on PATH, then erases pre-existing restic completions to ensure this script owns completion behavior.

## Dependencies and Integration Points

It depends on Fish builtins (`commandline`, `string`, `math`, `complete`, `type`) and the installed `restic` command's `__complete` endpoint. It integrates with Cobra's shell completion directive protocol. Active Help is disabled because this script does not support it for Fish.

## Risks and Edge Cases

- File extension and directory filtering directives are explicitly not supported; the script falls back to general file completion.
- The completion command is built as a string and executed with `eval`, so escaping from `commandline` is important.
- Fish's no-space behavior differs from Bash/Zsh; the script uses a two-completion trick for a single no-space match when needed.
- Cache globals must be cleared reliably or stale completions could leak between attempts.

## Test Signals

Manual Fish completion tests and regenerated completion comparisons are the main signals. Commands using dynamic completion should be tested for prefix filtering, flag-with-equals completion, no-file-completion, and keep-order behavior.
