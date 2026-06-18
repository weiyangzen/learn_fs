# sources/sync-backup/borg/src/borg/archiver/undelete_cmd.py

Purpose: implements `borg undelete`, restoring soft-deleted archive entries in the manifest before compaction permanently frees their objects.

Important APIs: `UnDeleteMixIn.do_undelete(args, repository)` loads the manifest with delete compatibility, selects one deleted archive by name or a filtered list of deleted archives, requires an explicit archive match when undeleting all, calls `manifest.archives.undelete_by_id(id)`, optionally logs each archive, writes the manifest if anything changed, and reports done/aborted/dry-run. `build_parser_undelete(...)` adds `--dry-run`, `--list`, archive filters, and optional archive name.

Control flow and state: the command uses `with_repository(manifest=False)` so it can explicitly call `Manifest.load(repository, (Manifest.Operation.DELETE,))`. In non-dry-run mode, successful undeletes are persisted by `manifest.write()`. It changes manifest archive deletion state only; chunk/object reclamation is governed by compaction elsewhere.

Dependencies and integration: uses archive formatting, `CommandError`, deleted-aware manifest archive selection, logging category `borg.output.list`, and common archive filter parser helpers.

Risks: accidentally undeleting every deleted archive is guarded by requiring `-a 'sh:*'` or another selector when no name/range/filter is given. If compaction has already removed data, undelete cannot reconstruct it; this file only exposes the manifest operation.

Test signals: cover name-based undelete, filter-based undelete, dry-run not writing, list messages, explicit-all safety error, missing archive warning path, and no-op behavior when no deleted archives match.
