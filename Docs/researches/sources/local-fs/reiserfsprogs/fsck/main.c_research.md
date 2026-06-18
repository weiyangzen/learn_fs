# File Research: sources/local-fs/reiserfsprogs/fsck/main.c

Main program and orchestrator for `reiserfsck`.

Command-line modes:
- `--check`
- `--fix-fixable`
- `--rebuild-sb`
- `--rebuild-tree`
- `--rollback-fsck-changes`
- `--clean-attributes`
- auto modes `-a` / `-p`
- version/no-op mode `-V`

Important options:
- Journal device, bad-block file, logfile/nolog, adjust-size, quiet, yes, force.
- Hidden/expert options include external bitmap scan, pass dump, whole-partition scan, hash override, rollback data, background mode, and no-journal-available.

Major orchestration:
- `parse_options`: validates mode/option combinations and fills `fsck_data`.
- `warn_what_will_be_done`: prints mode-specific warnings and asks for confirmation.
- `prepare_fs_for_check`: reopens read-write, rejects rw-mounted filesystems, handles ro-mounted restrictions, checks/replays journal.
- `check_fs`: standard check/fix-fixable path; opens bitmap, calls `check_fs_tree`, runs `semantic_check`, updates fs state and exit code.
- `auto_check`: lightweight boot-time check based on superblock state, clean unmount state, mount count, check interval, bitmap sanity, and root-tree scan.
- `rebuild_tree`: runs pass0, pass1, pass2, semantic pass, lost+found, and pass4, with resume support.
- `clean_attributes`: validates filesystem state and format, then clears stat-data attribute garbage.
- `fsck_rollback`: restores saved rollback blocks.
- `main`: sets terminal width, rlimit, background handling, opens filesystem/journal/badblocks, registers DMA monitoring, and dispatches mode.

Safety/integrity behavior:
- Replays journal before checks when possible and unmounted.
- Refuses rw-mounted filesystems.
- Locks memory when modifying ro-mounted filesystems.
- Marks fatal/error/consistent states in the superblock.
- Updates v2 last-check, mount count, max mount count, and check interval on success.
- Monitors DMA mode/speed changes and warns about hardware issues.

Rebuild resume:
- Uses superblock fsck state and pass dump magic to resume from pass0, pass1, tree-built, semantic, lost+found, or pass4 states.

Notable risks/quirks:
- Uses intentional switch fallthrough in `rebuild_tree` to continue passes.
- Background mode forks but still warns that confirmations may be needed from stdin.
- Auto check may switch into fix-fixable mode by falling through after `auto_check`.
