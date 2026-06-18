# sources/sync-backup/kopia/internal/completeset/complete_set.go

Purpose: detects complete groups of blob metadata following Kopia's `<prefix>-s<set>-c<count>` naming convention.

Important APIs/types/functions: `FindFirst`, `ExcludeIncomplete`, and `FindAll`.

Control flow: `FindAll` scans metadata in input order. Malformed names or malformed counts are emitted as singleton complete sets. Well-formed entries are grouped by set id (`s...`), and a group is emitted as soon as its observed length reaches the declared count. `FindFirst` returns the first emitted complete set; `ExcludeIncomplete` flattens all emitted sets.

State and persistence behavior: no persistent state. Output ordering depends on input order and on the first moment a set becomes complete.

Dependencies/integration: used by epoch manager to ignore incomplete/crashed compaction blob sets.

Risks/test signals: the parser only examines split parts 1 and 2, so prefixes containing dashes do not match the documented convention. Duplicate or over-complete sets can produce surprising grouping. Tests cover empty, malformed, complete, incomplete, and competing sets.
