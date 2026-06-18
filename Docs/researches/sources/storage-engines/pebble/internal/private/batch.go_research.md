<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/private/batch.go -->
# sources/storage-engines/pebble/internal/private/batch.go

Purpose: exposes a package-private hook for tests needing sorted iterators over batch mutations without making the batch internals public.

Important API: variable `BatchSort`, a function accepting an opaque batch-like `interface{}` and returning point, range-delete, and range-key iterators.

Control flow and state: no local control flow. The variable is assigned elsewhere, likely by the main Pebble package or tests, and consumers call it through the `internal/private` import boundary.

Persistence and integration: integrates with `base.InternalIterator` and `keyspan.FragmentIterator`. State is global process state, so tests must manage assignment ordering and cleanup. Risks include nil `BatchSort` panics if called before initialization, type assertion risks in the implementation behind the hook, and global mutation causing test coupling. There are no tests in this file; it is a narrow dependency-inversion point.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/private/batch.go -->
