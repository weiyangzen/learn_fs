<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ext.go -->
# sources/sync-backup/git-lfs/commands/command_ext.go

Purpose: implements `git lfs ext` and `git lfs ext list`, printing configured custom LFS extension clean/smudge commands and priorities.

Important APIs/types/functions: `extCommand`, `extListCommand`, `printAllExts`, `printExt`, `cfg.Extensions`, `cfg.SortedExtensions`, and `config.Extension`.

Control flow: the root command prints all extensions; `list` with no args does the same, while named args fetch matching entries from `cfg.Extensions()` and print them. Each extension emits name, clean command, smudge command, and priority.

State and persistence behavior: read-only; output is diagnostic. Missing named extensions resolve to zero-value `config.Extension` and are still printed.

Dependencies/integration points: depends on Git LFS extension configuration and command registration. Extensions affect clean/smudge/migrate/pointer behavior elsewhere.

Risks and test signals: risks include poor error reporting for unknown extension keys and direct stdout printing for sort errors. Test signals include no extensions, multiple sorted extensions, named extension lookup, and invalid extension config from `SortedExtensions`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ext.go -->
