# sources/sync-backup/syncthing/lib/sliceutil/sliceutil.go

Purpose: generic slice helpers for order-preserving removal and mapping.

Important APIs and control flow: `RemoveAndZero` shifts elements left from index `i+1`, writes the zero value into the old tail slot, and returns the slice shortened by one. This avoids retaining removed references in the backing array. `Map` allocates a result slice with the same length and applies a conversion function element by element.

State and persistence: pure in-memory helpers; `RemoveAndZero` mutates the input backing array.

Dependencies and integration: no external dependencies. Generic constraints preserve named slice types for removal while `Map` returns a plain `[]R`.

Risks: no bounds checks beyond Go's natural panics. Callers must understand that the original slice backing array is modified. Tests cover integer removal but not reference retention, named slice types, or `Map`.
