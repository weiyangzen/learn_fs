# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr.c

## Purpose
Core NVMe-oF controller implementation for SPDK’s target: connection setup, virtual controller properties, admin command handling, I/O dispatch, qpair lifecycle, async events, migration data, ANA, reservations, passthrough, and public request/controller helpers.

## Main Responsibilities
- Creates and destroys `spdk_nvmf_ctrlr` instances for admin connect requests.
- Validates fabric Connect capsules, host access, queue sizes, controller IDs, listener affinity, and duplicate QIDs.
- Manages qpair association, controller qpair masks, admin/I/O queue enablement, and delayed duplicate-QID retry.
- Maintains keep-alive, association, shutdown/reset, and controller fatal-state behavior.
- Implements property get/set for virtual NVMe registers: CAP, VS, CC, CSTS, NSSR, AQA, ASQ, ACQ, and CRTO.
- Handles admin commands: Identify, Get Log Page, Abort, Get/Set Features, AER, Keep Alive, and selected passthrough/custom admin paths.
- Handles fabric commands: Connect, Property Get/Set, and Authentication Send/Recv.
- Dispatches I/O commands to bdev or passthrough paths, including reservation checks, ANA checks, fused compare/write, zcopy, ZNS, and copy.
- Completes requests, tracks outstanding management and namespace I/O, and coordinates subsystem pause/resume accounting.
- Provides public helpers for bdev lookup, request buffers, command/response accessors, controller ID/subsystem access, custom admin handlers, and DIF context retrieval.

## Controller Lifecycle
- `nvmf_ctrlr_create()` allocates controller state, initializes identify/controller data, feature defaults, visible namespace bit array, virtual register state, listener association, and qpair mask.
- Admin qpair addition is routed to the subsystem thread, then controller thread, then poll group thread for connect response completion.
- `nvmf_ctrlr_destruct()` removes the controller from its subsystem and asynchronously frees qpair masks, logs, pending async events, visible namespace state, and controller memory.
- CC disable or shutdown starts I/O qpair disconnect across poll groups, uses timers for reset/shutdown deadlines, and may reset bdev namespaces on timeout.
- NSSR dispatches namespace subsystem reset or bdev reset and disables all controllers in the subsystem.

## Admin and Fabric Command Flow
- `spdk_nvmf_request_exec()` first checks subsystem/namespace active state and qpair state, queues inactive work if needed, inserts the request into outstanding, then routes to fabric, admin, or I/O handlers.
- Fabric Connect is valid before a qpair has a controller; once connected, admin queues allow property and authentication commands, while I/O queues only allow authentication fabric commands.
- Admin commands are rejected if sent while CC.EN is disabled, if fused, or if controller-scoped commands include an NSID.
- Discovery controllers are restricted to Identify, Get Log Page, Keep Alive, Get/Set Features, and AER.
- Custom admin handlers can intercept opcodes; passthrough admin commands are routed to a namespace bdev when configured.

## Identify and Log Pages
- Identify Controller populates fabric, discovery, NVM, ANA, optional command, reservation, and copy capability fields from transport/subsystem/controller state.
- Identify Namespace delegates bdev-derived namespace data to `ctrlr_bdev.c`, then optionally merges selected physical NVMe identify fields for passthrough bdevs.
- Supports active namespace lists, namespace ID descriptors, I/O command-set-specific Identify data for NVM/ZNS, I/O command-set vectors, and independent namespace data.
- Log pages include supported log pages, firmware slot, ANA, command effects, changed namespace list, reservation notification, feature ID effects, discovery log, and selected zero-filled/placeholder pages.
- Async event masks prevent repeated notices until the corresponding log page is read with RAE clear behavior.

## Feature Handling
- Supports arbitration, power management, temperature threshold validation, error recovery, volatile write cache, number of queues, interrupt vector configuration readback, write atomicity, async event config, keep-alive timer, host identifier, reservation notification mask/persistence, and host behavior support.
- Saveable feature requests are rejected.
- ANA inaccessible/persistent-loss/change states can convert certain namespace-affecting Get/Set Features into path status errors.
- Volatile write cache disabling is rejected as not changeable because SPDK cannot force backend cache bypass/drain semantics.
- Number of queues cannot be changed after I/O qpairs are active and returns the preconfigured queue count.

## I/O Dispatch
- `nvmf_ctrlr_process_io_cmd()` validates CC.EN, namespace visibility/bdev presence, ANA path state, and reservation conflicts.
- Standard commands map to bdev handlers: read, write, flush, compare, write zeroes, DSM, copy, and reservation operations.
- Reservation commands are forwarded to the subsystem thread.
- Unsupported optional opcodes are rejected unless command passthrough is enabled and a passthrough namespace exists.
- Fused compare/write enforces sequence and opcode rules, stores the first request on the qpair, and completes both requests consistently.
- Zcopy is only used for READ/WRITE on non-admin queues, when transport zcopy is enabled and the namespace supports it.

## Async Events and Reservations
- AER requests are stored up to `SPDK_NVMF_MAX_ASYNC_EVENTS`; pending events are queued if no AER is outstanding.
- Provides notices for namespace attribute changes, ANA changes, reservation log availability, discovery log changes, and error events.
- Reservation notification logs are capped at 255 queued pages and include per-namespace mask filtering.
- Reservation conflict checks enforce holder/registrant rules before I/O execution.

## Migration
- Saves/restores controller virtual registers, features, controller ID, ACRE state, pending async events, AER command IDs, and notice mask through `spdk_nvmf_ctrlr_migr_data`.
- Uses size fields and copy helpers for version-tolerant migration data handling.
- Includes a static assertion on `struct spdk_nvmf_ctrlr` size to force migration-field review when the structure changes.

## Storage Relevance
This file is the central NVMe-oF target control plane and request dispatch layer. It determines how remote NVMe hosts connect, authenticate, observe controller/namespace capabilities, issue storage I/O, receive async namespace/path/reservation events, and interact with bdev-backed storage.

## Risks / Notes
- Many operations are thread-affine and use `spdk_thread_send_msg()` or `spdk_for_each_channel()`; correctness depends on executing controller, subsystem, and poll-group work on the expected threads.
- Request completion performs important accounting and namespace/passthrough NSID restoration; bypassing it would corrupt pause/resume or outstanding I/O state.
- ANA, reservation, and subsystem pause states can queue or reject otherwise valid commands.
- Passthrough paths intentionally rewrite NSID and must restore it before accounting and completion.
