# sources/sync-backup/bup/lib/bup/cmd/validate_refs.py

## Purpose
`validate_refs.py` validates selected or all repository refs for missing linked objects and malformed or abridged `.bupm` metadata.

## APIs and Control Flow
`expected_bup_entry_count_for_tree` counts expected metadata entries from tree data, treating `.bupd` chunked directories specially. `resolve_refs` maps VFS refs to object IDs and reports missing refs. `main(argv)` requires at least one validation mode unless both option values are `None`, opens `LocalRepo`, resolves refs, defines `for_item` for `find_live_objects`, reports missing objects, parses `.bupm` streams with `Metadata.read`, compares counts to expected tree entries, and returns `EXIT_FAILURE`, `EXIT_FALSE`, or `EXIT_TRUE` according to severity.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies include `bup.gc.count_objects/find_live_objects`, `vfs`, `git.walk_object` behavior, metadata parsing, `tree_data_reader`, and pack idx broad existence checks when `--links` is enabled. It integrates with validation wrappers and GC's mark traversal. Risks include incomplete missing-object lists without `--links`, unsupported VFS item kinds, exception escalation for unparsable `.bupm`, and nuanced exit codes. Test signals include all/no refs, missing ref handling, missing object notices, extra vs abridged bupm counts, `.bupd` handling, and default option behavior.
