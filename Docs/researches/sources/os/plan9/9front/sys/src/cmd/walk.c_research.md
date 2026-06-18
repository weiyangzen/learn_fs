# File Research: sources/os/plan9/9front/sys/src/cmd/walk.c

Recursive Plan 9 file tree walker with selectable output fields, depth bounds, filtering, and loop detection.

Key behavior:
- Command flags select files vs directories, temporary-only entries, executable-only entries, unbuffered output, depth ranges, and stat-format fields.
- `walk()` recursively opens directories, reads `Dir` batches, skips `.`/`..`, detects already-seen directory qids/devices, and avoids descending past `maxdepth`.
- `dofile()` prints fields selected by `stfmt`, including owner/group/muid, times, name, path, qid, size, mode, device, and server type.
- `slashslash()` normalizes repeated slashes without full `cleanname()` behavior when `-C` is used.
- Default format is path-only output.

Notable dependencies:
- Plan 9 `Dir`, qid fields, `dirread`, `dirstat`, `dirmodefmt`, and libString.

Research notes:
- Cycle detection is ancestry-based and compares qid path/type plus device.
- `maxdepth` is incremented after parsing so user-facing depth semantics differ from the internal starting depth of 1.
