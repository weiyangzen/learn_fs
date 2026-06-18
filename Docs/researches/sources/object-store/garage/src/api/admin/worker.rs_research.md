## sources/object-store/garage/src/api/admin/worker.rs

Purpose: exposes local background worker inspection and runtime worker-variable get/set APIs.

Important APIs/types/functions: `RequestHandler` impls for `LocalListWorkersRequest`, `LocalGetWorkerInfoRequest`, `LocalGetWorkerVariableRequest`, and `LocalSetWorkerVariableRequest`; helper `worker_info_to_api`.

Control flow: listing obtains `admin.background.get_worker_info()`, filters by `busy_only` and `error_only`, maps worker state and status into API response structs. Get-by-id looks up a worker ID or returns `NoSuchWorker`. Variable reads query one named variable or all `garage.bg_vars`; writes call `garage.bg_vars.set`.

State/persistence: reads background worker runtime state and mutable background variables. Variables may influence worker behavior outside this file.

Dependencies/integration: depends on `garage_util::background::{WorkerInfo, WorkerState}`, `garage.bg_vars`, and admin API response types.

Risks: setting arbitrary worker variables is an operational control surface and must remain admin-token protected upstream. Worker IDs are runtime indices and may change. `last_error.secs_ago` uses saturating time arithmetic from `now_msec`.

Test signals: no local tests; behavior is straightforward mapping over background manager state.
