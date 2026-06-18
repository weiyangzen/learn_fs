# sources/storage-engines/tikv/components/engine_panic/src/checkpoint.rs

Purpose: Panic skeleton for checkpoint creation and database merge support.

Important APIs and types: `PanicEngine` implements `Checkpointable` with associated `PanicCheckpointer`. `PanicCheckpointer` implements `Checkpointer::create_at`.

Control flow and state: `new_checkpointer`, `merge`, and `create_at` panic. There is no persisted checkpoint state.

Dependencies and integration: Uses `engine_traits::{Checkpointable, Checkpointer}` and `std::path::Path`. Documents that real engines must create checkpoint directories and optionally Titan outputs.

Risks: Accidental invocation panics. The imported `core::panic` is redundant but harmless.

Test signals: No local tests.
