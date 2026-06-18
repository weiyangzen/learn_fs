# sources/storage-engines/tikv/components/engine_panic/src/db_vector.rs

Purpose: Panic implementation of the database value vector trait.

Important APIs and types: `PanicDbVector` implements `DbVector`, `Deref<Target=[u8]>`, and `PartialEq<&[u8]>`.

Control flow and state: `deref` panics, so `PartialEq` also panics when it dereferences `self`. No buffer is stored.

Dependencies and integration: Serves as associated `DbVector` for `PanicEngine` and `PanicSnapshot` peek operations.

Risks: Any attempted value inspection panics. The equality impl is syntactically useful but not operational.

Test signals: No tests.
