<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go

This file adapts Google fswalker to the robustness comparer contract. `WalkCompare` has global diff filters that ignore expected restore differences such as times, root directory rename, directory size, and UID/GID changes from zero.

`Gather` walks a path with hashing and returns marshaled protobuf data. `Compare` unmarshals prior walk data, walks the restored path, generates a report, filters modified diffs, validates there are no added/deleted/modified/error entries, and writes summary plus JSON report on failure. Helpers clear hostname, reroot paths relative to the source root, print summaries, and validate reports.

State is serialized walk protobuf bytes and transient reports. Dependencies are `github.com/google/fswalker`, protobuf, reporter/walker wrappers, and filter semantics. Risks include filters hiding real metadata regressions, report JSON being huge, path reroot errors, and hashing size limits in walker policy. Tests cover gather/compare, filters, validation, and rerooting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go -->
