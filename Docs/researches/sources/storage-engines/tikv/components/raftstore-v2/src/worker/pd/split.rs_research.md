# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/split.rs

Purpose: this file handles PD-assisted region split requests and auto-split execution for raftstore-v2.

Important APIs/functions: `new_batch_split_region_request` builds a batch-split admin request. Runner methods are `handle_ask_batch_split`, private `ask_batch_split_imp`, `handle_report_batch_split`, and `handle_auto_split`.

Control flow: explicit ask-batch-split validates non-empty keys, asks PD for new region/peer IDs, then builds a `BatchSplit` admin request and sends it through `StoreRouter` with the optional response channel. Reporting split completion sends `report_batch_split` asynchronously. Auto-split iterates `SplitInfo` values, fetches current region metadata from PD, and either asks for a load-based single-key split or leaves half-split range handling as TODO.

State and persistence: this worker does not persist split state. PD allocates IDs; the actual split is persisted by the peer after the routed admin command is proposed and applied.

Dependencies/integration: depends on PD client `ask_batch_split`, `report_batch_split`, `get_region_by_id`, admin request helper `send_admin_request`, `StoreRouter`, and raftstore auto-split `SplitInfo`.

Risks: if PD ID allocation fails, split is only logged and not retried here. `zip(split_keys, ids)` assumes PD returns matching ID count. Auto half-split is not implemented, so range-only auto split info is ignored.

Test signals: no local tests. Split behavior is covered by raftstore split/admin integration tests.
