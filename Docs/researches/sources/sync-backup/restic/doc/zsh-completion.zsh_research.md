# sources/sync-backup/restic/doc/zsh-completion.zsh

## Purpose

This generated Zsh completion script integrates restic with Zsh's completion system. It delegates to restic's Cobra `__complete` endpoint, interprets completion directives, supports Active Help, and maps candidates into Zsh `_describe`, `_files`, and `_arguments` calls.

## Important APIs, Types, and Functions

- `#compdef restic` and `compdef _restic restic` register the completion function.
- `__restic_debug` writes diagnostics to `BASH_COMP_DEBUG_FILE` when set.
- `_restic` is the main completion function. It defines Cobra directive constants, truncates `words` to the cursor position, detects flag-with-equals prefixes, constructs and evaluates the `__complete` request, parses the trailing directive line, separates Active Help lines, builds `completions`, and dispatches to the right Zsh completion primitive.
- Directive handling covers error, no-space, no-file-completion, file-extension filtering, directory filtering, and keep-order.
- The final guard runs `_restic` only when the function is invoked by Zsh completion rather than merely sourced/evaluated.

## Control Flow

On completion, `_restic` trims the command word list to `CURRENT`, inspects the current/last parameter, and appends an empty argument if the cursor follows a space. It calls the active restic binary with `__complete`, then reads the last output line to find a colon-prefixed directive. It loops over completion lines, handling `_activeHelp_ ` entries separately through `compadd -x`, converts tab-separated descriptions to the colon format expected by `_describe`, and escapes colons in completion values.

If the directive requests extension filtering, it builds an `_files -g` command. If it requests directory filtering, it optionally `pushd`s into the specified subdirectory and uses `_files -/`. Otherwise it calls `_describe`, optionally with `-S ''` for no-space and `-V` for keep-order. If `_describe` finds nothing and file completion is allowed, it falls back to `_files`.

## State and Persistence Behavior

All state is local to a Zsh completion invocation. It does not persist files except optional debug logging. It may temporarily change directories for directory-filtered completion and restores the prior directory with `popd`.

## Dependencies and Integration Points

It depends on Zsh completion functions (`compdef`, `compadd`, `_describe`, `_arguments`, `_files`) and the installed restic binary's Cobra completion endpoint. It supports Cobra Active Help markers, unlike the Bash/Fish scripts in this subset.

## Risks and Edge Cases

- The script uses `eval` for the request command and for `_describe` invocation with dynamically assembled options.
- Correct colon escaping and tab-to-colon conversion are required for Zsh descriptions.
- Directory filtering temporarily changes directories and must always restore state when a subdir was used.
- Docker/package installs must place this file in a location loaded by Zsh's completion path.

## Test Signals

Manual Zsh completion tests should cover descriptions, Active Help display, `--flag=` prefixes, extension filtering, directory-only filtering, no-space, no-file-completion, and keep-order candidates. Regeneration by `restic generate --zsh-completion` should match committed output.
