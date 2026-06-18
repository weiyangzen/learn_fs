## sources/sync-backup/kopia/internal/bigmap/bigmap_set.go

Purpose: exported set abstraction backed by `internalMap` without values.

Important APIs/types/functions: `Set`, `NewSet`, `NewSetWithOptions`, `Put`, `Contains`, and `Close`.

Control flow, state, and persistence: `Put` delegates to `inner.PutIfAbsent(ctx, key, nil)` and returns whether the key was newly added. No deletion or iteration is supported. State is in-memory/tempfile-backed through `internalMap`.

Dependencies and integration points: useful for large deduplication/member checks where keys are well-distributed binary IDs.

Risks and test signals: inherits key-length panics and append-only memory growth from `internalMap`. Tests cover duplicate insertion, growth, and panic conditions.
