# File Research: sources/virtualization/virtiofsd/src/vhost_user.rs

## Purpose

This file implements the vhost-user backend for virtio-fs. It connects guest virtqueues to the FUSE `Server`, negotiates virtio/vhost-user features, supports optional threaded request handling, exposes virtio-fs config, and coordinates device state save/load for migration.

## Main Constants And Types

- `QUEUE_SIZE`: 32768 descriptors.
- `REQUEST_QUEUES`: one request queue is supported.
- `NUM_QUEUES`: high-priority queue plus request queue.
- `HIPRIO_QUEUE_EVENT`, `REQ_QUEUE_EVENT`: device event indices.
- `MAX_TAG_LEN`: 36-byte virtio-fs tag limit.
- `LoggedMemory`: guest memory with dirty bitmap regions.
- `LoggedMemoryAtomic`: atomic guest memory wrapper.
- `Error`: backend setup and queue-processing failures.
- `VhostUserFsThread<F>`: internal per-backend state: guest memory, `Server<F>`, backend request FD, event-idx flag, and optional thread pool.
- `VirtioFsConfig`: packed virtio-fs config containing tag and request queue count.
- `PremigrationThread`: background serialization-preparation handle and cancellation flag.
- `VhostUserFsBackendBuilder`: builder for thread pool size and tag.
- `VhostUserFsBackend<F>`: public vhost-user backend implementing `VhostUserBackend`.

## Backend Construction

`VhostUserFsBackendBuilder` defaults to no thread pool and no tag. It can set:

- `thread_pool_size`: `0` means serial processing.
- `tag`: optional virtio-fs tag; when present the backend advertises `CONFIG`.

`build(fs)` creates a `VhostUserFsThread` wrapped in `RwLock`, plus migration state locks.

`VhostUserFsThread::new()` creates the `Server`. If a thread pool is requested, it first tests `unshare(CLONE_FS)` in the single-threaded setup phase. Worker threads call `unshare(CLONE_FS)` after start so xattr operations can change FS context without sharing it across threads.

## Queue Processing

Two processing modes exist.

Serial mode:

- `handle_event_serial()` picks the high-priority or request vring.
- `process_queue_serial()` collects available descriptor chains, creates `Reader` and `Writer`, calls `server.handle_message()`, and returns descriptors to the used ring.

Thread-pool mode:

- `handle_event_pool()` picks the vring by event.
- `process_queue_pool()` iterates available chains and spawns one async task per chain.
- Each task clones guest memory, server, backend request handle, vring, and descriptor chain; then it creates `Reader`/`Writer`, calls `server.handle_message()`, and returns the descriptor.

Both modes use `return_descriptor()` to add a used element and signal the used queue. With `EVENT_IDX`, it checks `needs_notification()` before signaling. Event handlers loop disable/process/enable while event-idx indicates more work may have arrived.

## VhostUserBackend Implementation

The backend reports:

- `num_queues()`: 2.
- `max_queue_size()`: 32768.
- `features()`: virtio version 1, indirect descriptors, event idx, protocol features, and log-all.
- `protocol_features()`: multiqueue, backend requests, backend send FD, reply ack, configurable memory slots, log shared memory FD, device state, reset device, and optional config.

Important methods:

- `get_config(offset, size)`: returns a sliced/padded `VirtioFsConfig` with the UTF-8 tag and one request queue.
- `acked_features(features)`: starts or cancels premigration preparation depending on `LOG_ALL`.
- `reset_device()`: calls `Server::destroy()`.
- `set_event_idx(enabled)`: stores negotiated event-idx mode.
- `update_memory(mem)`: stores guest memory.
- `handle_event(...)`: validates `EventSet::IN` and dispatches serial or pool handling.
- `exit_event(...)`: creates an eventfd consumer/notifier pair.
- `set_backend_req_fd(vu_req)`: stores backend request channel.
- `set_device_state_fd(...)`: starts save/load state transfer.
- `check_device_state()`: joins the migration thread and reports its result.

## Migration Flow

Premigration:

- When `LOG_ALL` is acknowledged, `acked_features()` starts a background thread calling `server.prepare_serialization(cancel)`, unless one is already running.
- When `LOG_ALL` is cleared, any premigration thread is canceled and joined.

State save:

- `do_set_device_state_fd(SAVE, STOPPED, file)` takes the premigration thread, joins it if present, or warns and runs `prepare_serialization()` synchronously if no premigration happened.
- It then calls `server.serialize(file)` in a migration thread.

State load:

- `do_set_device_state_fd(LOAD, STOPPED, file)` cancels any premigration thread and starts a migration thread calling `server.deserialize_and_apply(file)`.

Completion:

- `do_check_device_state()` requires a prior migration thread and joins it. Missing migration state is treated as a protocol violation.

Only `VhostTransferStatePhase::STOPPED` is supported.

## Tag Config Behavior

If a tag is configured, the backend advertises the `CONFIG` protocol feature. `get_config()` asserts the tag is non-empty and at most 36 UTF-8 bytes, pads it with NUL bytes to `MAX_TAG_LEN`, and returns the requested config slice padded to the requested size.

`Error::InvalidTag` documents the tag constraints, though validation is expected before `get_config()`.

## Integration Points

This module integrates with:

- `crate::server::Server`, which handles FUSE protocol messages.
- `crate::filesystem::{FileSystem, SerializableFileSystem}` as the backend abstraction.
- `crate::descriptor_utils::{Reader, Writer}` for guest descriptor chains.
- `vhost_user_backend::{VhostUserBackend, Vring*}` for event and vring mechanics.
- `vhost::vhost_user::Backend` for backend requests.
- `vm_memory` and `BitmapMmapRegion` for guest memory and migration logging.
- `futures::executor::ThreadPool` for optional parallel request processing.

## Important Invariants

- Guest memory must be configured before queue processing.
- Only high-priority queue index 0 and request queue index 1 are valid events.
- Queue processing unwraps descriptor reader/writer and server errors inside worker paths, so these are treated as unrecoverable for that task.
- With thread-pool mode, descriptor completion happens asynchronously after `handle_event_pool()` returns.
- `event_idx` mode requires repeated processing until enabling notification reports no more pending events.
- Migration state uses locks so only one premigration thread and one migration thread are tracked.

## Risks And Edge Cases

- Worker tasks use `unwrap()` after mapping errors; malformed descriptors or server errors can panic worker execution.
- Thread-pool mode clones and processes vring state asynchronously; correctness depends on `VringMutex` and descriptor ownership semantics.
- `acked_features()` cancellation behavior for `LOG_ALL` clearing is acknowledged as an interpretation rather than a guaranteed spec signal.
- If the frontend calls `check_device_state()` without a prior successful `set_device_state_fd()`, the backend returns `InvalidInput`.
- `get_config()` panics if called when no tag is configured, relying on feature negotiation to prevent that call.
