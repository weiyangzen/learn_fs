# sources/object-store/garage/src/db/lib.rs

Purpose: defines Garage's engine-neutral transactional key/value database API and internal adapter traits.

Important APIs/types/functions: `Db`, `Tree`, `Transaction`, `Error`, `TxOpError`, `TxError`, `TxResult`, `unabort`, `Db::{open_tree,list_trees,transaction,snapshot,import}`, `Tree` CRUD/iteration/range APIs, `Transaction` CRUD/iteration/on_commit APIs, internal traits `IDb`, `ITx`, `ITxFn`, and `TxFnResult`.

Control flow: `Db::transaction` wraps user closures in `TxFn`, delegates to the adapter, then reconciles adapter result with the closure's stored result. On successful commit, queued `on_commit` callbacks run after the adapter returns. `Db::import` rejects non-empty destination DBs, opens each source tree, and copies entries in a transaction while printing progress every 1000 items.

State and persistence: state is in adapter-specific trees. `Tree` is a lightweight handle with DB pointer and tree id. `on_commit` callbacks are volatile and run only after successful commit.

Dependencies and integration points: adapter modules are feature-gated; `open` is re-exported. Higher-level Garage tables rely on this stable contract for metadata persistence and transaction semantics.

Risks: `Db::transaction` has several subtle result combinations and panics on impossible states. Long imports happen inside one transaction per tree, which can stress memory/locks on large trees. Iterators expose boxed dynamic iterators and rely on adapters to preserve transaction lifetimes safely.

Test signals: `db/test.rs` validates CRUD, commit/abort, forward/reverse iteration, and ranges across adapters.
