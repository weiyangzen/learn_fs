# sources/storage-engines/tikv/src/server/service/batch.rs

Purpose: batches eligible normal-priority transactional `Get` and `RawGet` requests from batch-command streams, reducing scheduling overhead while preserving per-request responses and metrics.

Important APIs/types/functions: `ReqBatcher`; `BatcherBuilder`; `GetCommandResponseConsumer`; `future_batch_get_command`; `future_batch_raw_get_command`; batching constants.

Control flow: `BatcherBuilder::build` enables batching only when request batch size and per-worker queue depth justify it. `ReqBatcher` buffers gets/raw gets and flushes on threshold or final commit. Transactional gets create tracker tokens, record request sizes, and call `storage.batch_get_command`; raw gets call `raw_batch_get_command`. Consumers convert item results into protobuf responses, including region/key errors, scan detail, RU detail, values, not-found flags, and commit_ts. Whole-batch region errors are fanned out to all IDs.

State/persistence: transient request buffers and tracker tokens; no storage persistence except reads performed by storage APIs.

Dependencies/integration: used by KV batch command service; depends on storage batch APIs, tracker registry, response batch consumers, metrics, protobufs, and mpsc response channel. Risks include coarse group priority/source handling, warning-only dropped response channel, and uniform fan-out for whole-batch region errors. Unit tests verify commit_ts propagation/default zero.
