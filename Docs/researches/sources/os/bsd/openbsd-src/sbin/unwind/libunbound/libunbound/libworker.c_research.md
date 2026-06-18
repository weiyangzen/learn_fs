# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.c

Implements the libunbound worker used by the library API to execute DNS resolution and validation in foreground, background thread/process, or caller-supplied event-loop mode.

Major responsibilities:
- Builds a worker-local `module_env` from `ub_ctx`, including scratch region/buffer, random state, SSL context, comm base, outside network object, and mesh.
- Supports foreground blocking queries via `libworker_fg()`.
- Supports asynchronous background operation via `libworker_bg()`, using a thread when enabled or `fork()` where threading is unavailable/disabled.
- Supports event-loop integration through `libworker_create_event()` and `libworker_attach_mesh()`.
- Serializes/deserializes async commands and answers through context/tube helpers.

Query flow:
- `setup_qinfo_edns()` builds wire-format qname, EDNS DO settings, and advertised UDP size.
- Foreground/event/background paths first check local zones and authoritative downstream zones for immediate answers.
- Otherwise, queries are attached to the mesh with callbacks for completion.
- Completion callbacks fill `ub_result`, copy packet data as needed, mark DNSSEC status, record bogus reasons, and handle rate-limit indicators.

Result handling:
- `libworker_enter_result()` parses a DNS packet into query/reply structures, extracts answer RR data, canonical name, rcode, NXDOMAIN state, security state, bogus state, and TTL.
- `fill_res()` copies packed RRset RDATA into libunbound’s public result arrays and computes minimum TTL across answer CNAME/answer rrsets.
- Background answers are queued back to the application via the result pipe unless canceled or shutting down.

Network integration:
- `libworker_send_query()` allocates an outbound entry in the module query region and calls `outnet_serviced_query()`.
- `libworker_handle_service_reply()` validates basic DNS reply shape and reports success/timeout/error back to mesh.

Cleanup and compatibility:
- Worker deletion tears down mesh, scratch storage, random state, SSL context, outside network, and comm base.
- Allocation cleanup clears rrset and message cache slabhashes for allocator ID reuse.
- Provides assertion-only fake daemon-worker callbacks so function-pointer whitelist/linkage expectations are satisfied in libunbound builds.

Filesystem/storage relevance:
- No filesystem implementation. Relevant as resolver infrastructure using shared caches, slabhash-backed DNS data, event loops, threads/forked workers, and careful ownership across shared `ub_ctx` state.
