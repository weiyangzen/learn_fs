## sources/object-store/rustfs/crates/targets/src/runtime/tls/state.rs

Purpose: defines per-target TLS reload runtime state, immutable published state, watched input paths, and an admin/debug status snapshot.

Important APIs/types/functions: `TargetTlsInputSet` records CA path, client cert path, client key path, and `target_label`; `is_empty` detects no TLS paths. `TargetTlsPublishedState<M>` contains generation, fingerprint, material `Arc<M>`, and load timestamp. `TargetTlsRuntimeState<M>` owns `current` and `last_good` `ArcSwap`s, atomic attempt/success timestamps, `last_error`, and inputs. It exposes `new`, `current_generation`, `bump_generation`, `mark_attempt`, `mark_success`, and timestamp accessors. `TargetTlsStatusSnapshot` is serde-serializable for observability.

Control flow and state: `current` is the hot-path material pointer. `last_good` is updated only after successful publish and is intentionally preserved on failed reloads. Timestamp atomics use acquire/release ordering; error text uses `parking_lot::RwLock`.

Dependencies and integration points: used by adapter and coordinator. `ArcSwap` enables cheap, lock-free reads of current material by send paths.

Risks: `bump_generation` computes from the currently loaded generation but does not publish atomically with compare-and-swap; concurrent reload publishers could select the same generation if not externally serialized. The status snapshot includes file paths, which is useful operationally but may expose local paths through admin APIs.

Test signals: tests live in the coordinator module for state mutation semantics; shared runtime state has its own direct tests.
