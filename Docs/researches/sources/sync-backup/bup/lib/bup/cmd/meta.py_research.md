# sources/sync-backup/bup/lib/bup/cmd/meta.py

## Purpose
`meta.py` is a metadata archive utility. It can create, list, extract, start/finish extraction, or edit bup metadata streams independently of full repository save/restore operations.

## APIs and Control Flow
`open_input` and `open_output` map empty or `-` names to byte stdin/stdout. `main(argv)` prepends default `--paths --symlinks --recurse`, enforces exactly one action, sets `metadata.verbose`, and delegates to `metadata.save_tree`, `display_archive`, `start_extract`, `finish_extract`, `extract`, or archive iteration plus field mutation for `--edit`. `--edit` applies the last relevant user/group set/unset flag semantics while uid/gid are parsed as integers.

## State, Dependencies, Integration, Risks, Tests
Create/list/edit read and write archive streams; extract modes create filesystem paths and apply metadata. Dependencies are `bup.metadata`, byte streams, and `argv_bytes`. Integration points are `.bupm` metadata compatibility and restore-like ownership handling. Risks include private `_ArchiveIterator` use, destructive filesystem extraction, conflicting action/argument combinations, and stream output corruption if stdout is not flushed/wrapped. Test signals include one-action enforcement, stdin/stdout file handling, recurse/xdev/symlink flags, numeric-id extraction, edit ordering, and invalid uid/gid errors.
