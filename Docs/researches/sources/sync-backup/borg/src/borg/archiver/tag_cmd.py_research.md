# sources/sync-backup/borg/src/borg/archiver/tag_cmd.py

Purpose: implements `borg tag`, a write operation that edits archive tag metadata for one named archive or for archives selected by filter arguments.

Important APIs: `TagMixIn.do_tag(args, repository, manifest, cache)` is wrapped with `with_repository(cache=True, compatibility=(Manifest.Operation.WRITE,))`. It selects archive infos from `args.name` or `manifest.archives.list_considering(args)`, opens each `Archive`, applies `--set`, `--add`, and `--remove`, writes metadata through `archive.set_meta("tags", sorted_tags)`, updates the manifest archive index if the archive ID changed, and prints old/new short IDs. `build_parser_tag(...)` defines validators for archive names and tags plus common archive filters.

Control flow and state: tag mutation changes archive metadata, which changes the archive ID. The code deletes the old manifest archive entry when `old_id != archive.id`. `--set` has protective handling for special tags beginning with `@`: existing special tags are retained unless the user includes them in the `--set` list, preventing accidental removal of tags such as `@PROT`.

Dependencies and integration: uses `Archive`, `Manifest`, archive filter helpers, `bin_to_hex`, `archivename_validator`, and `tag_validator`. The command participates in repository compatibility checks through the decorator.

Risks: the `--set` special-tag guard silently skips assignment when it would clobber existing special tags, then still applies add/remove operations. Tests and UI should make this behavior clear. Because tags live in archive metadata, interrupted writes need manifest/archive persistence code to remain atomic.

Test signals: cover setting regular tags, adding/removing tags, preserving `@` tags on unsafe `--set`, allowing `--set` when existing special tags are included, filter-selected multi-archive tagging, and manifest deletion of old archive IDs after metadata rewrite.
