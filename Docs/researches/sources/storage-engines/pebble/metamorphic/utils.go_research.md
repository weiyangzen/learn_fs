<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/utils.go -->
## sources/storage-engines/pebble/metamorphic/utils.go

Purpose: provides low-level object ID and small collection helpers for the metamorphic framework.

Important APIs and types: `objTag` enumerates DB, batch, iterator, snapshot, and external object tags. `objID` packs a 4-bit tag and 28-bit slot. `makeObjID`, `tag`, `slot`, `String`, and `parseObjID` convert between packed IDs and textual IDs like `db1`, `batch0`, `iter3`, `snap2`, and `external4`. `objIDSlice` supports sort.Interface, removal, and random selection. `objIDSet.sorted` returns deterministic sorted IDs. `firstError` returns the first non-nil error.

Control flow: `parseObjID` special-cases legacy `db` to `db1`, then finds a known prefix and parses the numeric suffix. `objIDSlice.remove` swaps the removed element with the tail for O(n) deletion without preserving order. `sorted` copies map keys and sorts by packed ID.

State and persistence: no persistent state. The packed ID representation is in-memory but also defines the textual operation format consumed by parser and formatter.

Dependencies and integration: used throughout metamorphic parser, generator, operation execution, and object slot management. Depends on `math/rand/v2`, `sort`, string parsing, and Cockroach errors.

Risks and edge cases: `String` indexes `objTagPrefix` by tag and assumes valid tags. `parseObjID` accepts any parsed 32-bit slot and does not reject zero DB slots, leaving semantic validation to callers. Removal silently does nothing when the ID is absent.

Test signals: parser tests and generated operation round-trips indirectly exercise object ID formatting and parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/utils.go -->
