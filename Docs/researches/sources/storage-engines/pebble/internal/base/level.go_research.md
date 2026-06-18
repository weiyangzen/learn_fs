# sources/storage-engines/pebble/internal/base/level.go

Purpose: Encodes an optional LSM level as a compact value with a validity bit.

APIs and types: `Level`, `MakeLevel`, `Get`, `Valid`, and `String`.

Control flow and state: `MakeLevel` stores the numeric level plus a high valid bit. `Get` returns `(level, true)` only when the valid bit is set; otherwise `(0, false)`. `String` renders invalid levels as `?`.

Persistence and dependencies: No direct persistence. Used in runtime metadata/statistics such as cache access levels.

Integration points: Cache APIs accept `base.Level` to attribute metrics; other internal components can represent optional levels without pointers.

Risks: The representation is `uint8`; callers must avoid levels too large to fit after reserving the valid bit.

Test signals: No direct test in this subset; usage is simple and indirectly covered by cache/iterator metrics tests.
