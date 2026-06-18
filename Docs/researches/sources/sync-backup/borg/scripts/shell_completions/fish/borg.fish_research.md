# sources/sync-backup/borg/scripts/shell_completions/fish/borg.fish

## Purpose
This Fish shell completion script provides static and dynamic completions for the `borg` command. It enumerates top-level Borg commands, nested command groups such as `key`, `benchmark`, and `help`, common global options, and command-specific options for repository, archive, backup, restore, transfer, tar import/export, and server workflows. It is installed under Fish vendor completions and is user-facing CLI metadata rather than runtime Borg backup logic.

## Important APIs, Types, and Functions
- Fish `complete -c borg ...` declarations are the primary API. They associate subcommands, options, descriptions, argument candidates, file-completion behavior, and `-n` predicates with the `borg` command.
- `__fish_borg_seen_key`, `__fish_borg_seen_benchmark`, and `__fish_borg_seen_help` restrict second-level completions to the relevant command groups and prevent suggesting already-selected nested commands.
- `__fish_borg_archives` shells out to `borg repo-list --format="aid:{id:.8}{TAB}{archive} {start}{NEWLINE}"` to produce archive identifiers plus display metadata.
- `__fish_borg_archive_arg --argument command token_count` checks the tokenized Fish command line and current token to decide whether dynamic archive-name completions should be offered at a specific positional argument slot.
- Local candidate variables such as `sort_keys`, `files_cache_mode`, `compression_methods`, `recompress_when`, and `fuse_options` provide enumerated values for selected options.

## Control Flow
The file is declarative in broad sections: top-level command completions, subgroup predicate functions, common options, per-command option groups, and finally dynamic archive argument completion. Fish evaluates the `-n` predicates lazily while the user types. Most options are gated by `__fish_seen_subcommand_from <command>`, so command-specific options are suggested only after Fish sees the matching command token. At the end, the script erases default filename completions for archive-argument contexts, adds explicit `--no-files` completions for exact token positions, then adds high-priority archive suggestions from `__fish_borg_archives`.

## State and Persistence Behavior
The script itself persists no Borg state. Its dynamic archive completion reads repository state indirectly by invoking `borg repo-list`, which can prompt or fail depending on repository configuration, `BORG_REPO`, and authentication environment such as `BORG_PASSPHRASE`. It redirects errors to `/dev/null`, so completion failures are silent. The static option lists can become stale unless regenerated or manually kept in sync with argparse definitions.

## Dependencies and Integration Points
It depends on Fish built-ins and helper functions (`complete`, `commandline`, `__fish_seen_subcommand_from`, `__fish_is_first_token`, `string`, `test`, `count`) and on a working `borg` executable for archive listing. Its integration target is the CLI built by `src/borg/archiver/__init__.py` and command mixins under `src/borg/archiver/`. Several options mirror helpers in `_common.py`, including archive filters, include/exclude pattern options, common logging/repository flags, and command-specific options from modules such as `check_cmd.py` and `benchmark_cmd.py`.

## Risks and Edge Cases
- Drift risk is high: the script is manually enumerated and can diverge from argparse command definitions, option spelling, defaults, or new subcommands.
- The import-tar exclusion block is gated with `__fish_seen_subcommand_from recreate`, which looks suspicious because the preceding section is for `import-tar`; that likely prevents those completions from appearing for import-tar.
- Dynamic archive completion may be slow for large or remote repositories because it invokes `borg repo-list` during completion.
- Password-protected repositories only list archives when the needed authentication is already available, as noted in the file header.
- `__fish_borg_archive_arg` assumes token 1 is `borg` and token 2 is the command; aliases, wrappers, environment assignments, or `command borg` forms may not match.

## Test Signals
Useful tests include `fish -n borg.fish` syntax validation, interactive completion checks for every top-level command, parity checks against `borg --help`/subcommand help output, and targeted checks that archive-name completions appear only in the intended positional slots. Dynamic completion should be tested with empty, encrypted, local, and remote repositories. The likely import-tar predicate bug deserves a regression test that `borg import-tar --exclude` is suggested while `borg recreate --exclude` remains unaffected.
