# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.c

Parses tracker chunks from SKHT/debug telemetry.

Main behavior:
- Tracker data is split into 4096-byte chunks.
- Requires config structures:
  - `ablist_context_t`
  - `ablist_entry_t`
  - `tracker_entry_t`
- Validates chunk signature `0xab15ab15`.
- Walks linked entries via `next_entry_index`.
- Looks up tracker entry metadata in config under `Tracker.TrackerEntry.<hash>`.

Output:
- Adds `offset`, `size`, `chunks`, and `entries` to the target JSON object.
- Each entry may include name, file, line, time, arm id, hash, numeric level, level name, group, arg count, and named arguments.

Argument handling:
- Up to 31 args.
- Argument labels come from `descArgN` fields in config, otherwise fallback to `argN`.

Risks/notes:
- If tracker entry hash is unknown, the entry is skipped.
- Chunk count is `size / 4096`; trailing partial chunk bytes are ignored.
