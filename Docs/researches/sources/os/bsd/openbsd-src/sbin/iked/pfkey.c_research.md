# File Research: sources/os/bsd/openbsd-src/sbin/iked/pfkey.c

Read completely: 2124 lines.

Implements iked's PF_KEY v2 integration with the OpenBSD kernel IPsec stack. It maps IKEv2 algorithms/protocols to SADB constants, installs/deletes flows and SAs, obtains SPIs, groups bundled SAs such as IPCOMP+ESP, queries last-use/stat counters, handles decoupled operation, registers for kernel acquires/expires, and processes asynchronous PF_KEY messages.

State and maps:
- `sadb_msg_seq` is the single outstanding PF_KEY sequence counter; comments note only one message can be outstanding.
- `sadb_decoupled` suppresses most kernel writes while allowing GETSPI.
- `iked_rdomain` stores iked's routing domain for rdomain-switching SA installs.
- `pfkey_postponed` and `pfkey_retry` hold asynchronous kernel messages that could not be processed immediately.
- Constant maps translate IKEv2 encryption, integrity, and SA protocol IDs into PF_KEY SADB IDs.

Coupling and mapping:
- `pfkey_couple()` toggles kernel coupling for all known SAs and flows. Recoupling installs unloaded child SAs, bundled IPCOMP SAs, and flows; decoupling deletes loaded ones; then updates `sadb_decoupled`.
- `pfkey_map()` performs the generic IKE-ID to PF_KEY-ID lookup.

Flow management:
- `pfkey_flow()` constructs `SADB_X_ADDFLOW`/`SADB_X_DELFLOW` messages with source/destination flow addresses, masks, protocol, direction, optional local/peer tunnel addresses, identities, pre-NAT address adjustment, and optional rdomain extension.
- Address masks are generated from prefix lengths for IPv4/IPv6; ports become full masks when present.
- `pfkey_flow_add()` and `pfkey_flow_delete()` map SA protocol, call `pfkey_flow()`, and maintain `flow_loaded`.

SA management:
- `pfkey_sa()` constructs SADB ADD/UPDATE/DELETE messages with SA, source/destination/proxy addresses, keys, lifetimes, UDP encapsulation, tag, tap, sec(4) interface routing, ESN/tunnel flags, identities, and rdomain extensions.
- It uses policy lifetime hard/soft values, applies random 85-95% soft lifetime jitter, doubles IPCOMP addtime and clears byte lifetime, validates algorithm support, rejects missing keys except for compression/IPIP cases, and swaps identities for incoming `SADB_UPDATE`.
- MOBIKE address update uses internal action `IKED_SADB_UPDATE_SA_ADDRESSES`, emits a `SADB_UPDATE`, and may include a proxy address for the old peer.
- `pfkey_sa_lookup()` sends `SADB_GET`, optionally extracts `SADB_X_EXT_LIFETIME_LASTUSE` and `SADB_X_EXT_COUNTER`, and is wrapped by `pfkey_sa_last_used()`, `pfkey_sa_check_exists()`, and `pfkey_sa_sastats()`.
- `pfkey_sa_getspi()` sends `SADB_GETSPI` with source/destination and SPI range, then extracts the returned SA SPI.
- `pfkey_sagroup()` constructs `SADB_X_GRPSPIS` for bundled SAs, with special rdomain handling for incoming IPCOMP+ESP combinations.
- `pfkey_sa_init()` obtains a new kernel SPI.
- `pfkey_sa_add()` chooses ADD versus UPDATE based on allocation/load state, handles ADD timeout by checking whether the SA actually exists, retries local recoupling updates as ADD after `ESRCH`, optionally groups with a previous/bundled SA, and marks the child SA loaded.
- `pfkey_sa_update_addresses()` updates outbound SA peer addresses when MOBIKE peer address changed.
- `pfkey_sa_delete()` preserves counters via `pfkey_sa_sastats()`, deletes the SA, verifies deletion when needed, clears loaded state, and accumulates child counters into the parent IKE SA.
- `pfkey_flush()` flushes all SADB state.
- `pfkey_id2ident()` converts supported IKE ID types to SADB identity extensions using printable ID strings; unsupported ID types return `NULL`.

PF_KEY I/O:
- `pfkey_write()` ignores most writes while decoupled, temporarily removes the persistent socket event, writes the iovec with expected SADB length, waits for a reply, then re-adds the event.
- `pfkey_reply()` polls for a reply with `PFKEY_REPLY_TIMEOUT`, validates version, allocates/reads the full message, returns the matching pid/seq reply, ignores unrelated process replies, postpones asynchronous kernel messages, returns `-2` on timeout, and treats `EEXIST` as non-fatal for no-data operations.
- `pfkey_find_ext()` walks SADB extensions by chunk length and returns the requested extension type.

Initialization and async dispatch:
- `pfkey_socket()` is parent-process-only and opens the raw PF_KEY v2 socket or fatals.
- `pfkey_init()` records current rdomain, initializes the postponed-message timer, registers the persistent socket event, flushes SADB state, and registers for ESP and AH acquires.
- `pfkey_dispatch()` reads one async PF_KEY message, processes postponed messages first to preserve order, calls `pfkey_process()`, and queues the message for retry if processing reports busy.
- `pfkey_timer_cb()` retries postponed messages, moving still-busy entries to a retry queue and rearming the timer as needed.

Kernel event processing:
- `pfkey_process()` handles `SADB_ACQUIRE` by extracting the peer address, asking the kernel for the matching policy with `SADB_X_ASKPOLICY`, parsing source/destination flow addresses and masks, protocol direction, SA type, and peer endpoint, then calling `ikev2_child_sa_acquire()`.
- It handles `SADB_EXPIRE` by extracting the SA and soft/hard lifetime extension, mapping SA type to IKEv2 SPI metadata, and calling `ikev2_child_sa_rekey()` for soft expiry or `ikev2_child_sa_drop()` for hard expiry.
- It returns `-1` only for busy retry semantics from child SA handlers; malformed/unusable kernel messages are logged and considered consumed.

Risks and notes:
- PF_KEY is treated as unreliable; reply timeout returns a retry-style error, and ADD timeout recovery probes whether the SA exists.
- The single global sequence model assumes only one outstanding PF_KEY request.
- The repeated `PAD` macro/iovec construction relies on `IOV_CNT` being sufficient for every optional extension combination.
- Some unsupported identities are silently omitted from PF_KEY messages.
- Acquire parsing has a likely copy/paste oddity in destination mask handling where `flow_src` net flags are updated while processing destination masks.
