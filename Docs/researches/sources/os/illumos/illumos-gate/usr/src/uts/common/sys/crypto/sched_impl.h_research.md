# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/sched_impl.h

Internal scheduler structures for the kernel cryptographic framework. It defines synchronous/asynchronous request nodes, context lifetime tracking, software-provider queueing, request-id hashing, provider retry lists, bufcall/notify lists, and scheduler entry points.

Key elements:
- Defines request states `REQ_ALLOCATED`, `REQ_WAITING`, `REQ_INPROGRESS`, `REQ_DONE`, and `REQ_CANCELED`, plus synchronous/asynchronous call types.
- Fast-path macros distinguish direct software-provider execution from queued execution and derive allocation flags from request context.
- `kcf_prov_tried_t` tracks providers already attempted during failover/retry provider selection.
- Recovery macros classify retryable provider errors such as busy, device failure, memory, buffer-too-big, key-size range, and permission failures.
- `kcf_sreq_node_t` represents a synchronous request with CV/lock completion state, return value, parameter pointer, context, provider, and per-provider CPU mapping.
- `kcf_areq_node_t` represents an asynchronous request with saved parameters, callback request argument, context request chain links, turn-taking state, global software queue links, provider, tried-provider list, request-id hash links, completion CV, and reference count.
- Reference macros release async requests and KCF contexts when atomic counts reach zero.
- `kcf_dual_req_t` stores framework-generated chained requests for dual operations, including saved offset/length for continuation.
- Request IDs are partitioned across 16 tables and 512 hash buckets, with high-bit/counter layout designed to avoid wraparound collision checks.
- `kcf_context_t` embeds the provider-visible `crypto_ctx_t`, tracks references, in-use locking, async request chains, provider descriptors, mechanism entry, and second context for dual operations.
- `kcf_ctx_template_t` records provider handle, generation, allocation size, and provider template pointer for software context templates.
- Defines global software queue, software worker pool, crypto bufcall elements, notify-list elements, taskq sizing constants, and exported global queue/list locks.
- Declares scheduler/provider-selection routines including provider lookup, dual-provider lookup, request submission, common SPI submission, context allocation/free, notification walks, dual request allocation, and chained request callbacks.

Dependencies:
- Uses crypto API/SPI/internal provider descriptors and request parameters from `api.h`, `spi.h`, `impl.h`, `common.h`, and `ops_impl.h`.
- Integrates with kernel synchronization primitives, task queues, doors, atomics, condition variables, and provider CPU mapping.

Research notes:
- Context release is conditional: queued, busy, and buffer-too-small results keep contexts alive for provider completion or client retry.
- Async requests must copy request parameters because caller stack storage can disappear; synchronous requests can point at caller-owned parameters.
- `CHECK_FASTPATH` and special software-provider request handles control whether provider callbacks see `KM_SLEEP` or `KM_NOSLEEP` semantics.
