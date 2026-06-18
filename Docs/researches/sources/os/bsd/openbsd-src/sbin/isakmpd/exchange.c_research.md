# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.c

Core exchange manager for isakmpd. It owns exchange allocation, lookup, validation scripts, initiator/responder dispatch, finalization, retransmit bookkeeping, nonce/certificate request helpers, and high-level phase establishment.

Key responsibilities:
- Maintains a global hash table of `struct exchange` entries keyed by cookies and, for phase 2, message ID.
- Defines payload validation scripts for Base, Identity Protection/Main Mode, Authentication Only, Aggressive, Informational, Transaction, and DOI-specific exchange types.
- `exchange_run()` drives the exchange state machine by alternating between outbound generation and inbound validation/DOI handler execution. It advances `step` and `exch_pc`, saves last received/sent messages, registers post-send finalization, and updates crypto IVs after encrypted inbound messages.
- `exchange_establish_p1()` creates initiator phase-1 exchanges from configuration, generates initiator cookies, creates the initial ISAKMP SA, handles `ikecfg` finalization chaining, and starts the state machine.
- `exchange_establish_p2()` creates phase-2 exchanges under an existing ISAKMP SA, copies cookies, creates a random message ID, enables encryption/NAT-T flags, optionally creates child SAs, and starts the state machine.
- `exchange_setup_p1()` and `exchange_setup_p2()` create responder-side exchanges from inbound messages after checking policy, DOI, exchange type, duplicate active exchange state, and cookies.
- `exchange_finalize()` transfers negotiated state into SAs, marks SAs ready, copies IDs and phase-1 keystate/authentication material, handles replaced SAs, runs DOI and caller finalizers, detaches SAs from the exchange, and starts DPD after phase 1 if the peer advertised support.
- `exchange_free()`/`exchange_free_aux()` release messages, nonce/ID buffers, DOI data, keys, certs, KeyNote sessions, cert request lists, hash links, finalizers, and unfinalized SAs.
- Nonce helpers generate and save 8..256 byte nonces.
- Certificate request helpers save inbound CERTREQs, reflect acceptable CERTREQs, obtain certs, add CERT/CERTREQ payloads, and free ACA lists.
- `exchange_establish()` is the top-level config-driven entry point for phase 1 or phase 2, including recursive phase-1 establishment when a phase-2 request lacks an ISAKMP SA.

Important data flow:
- `exchange->data` is DOI-specific storage allocated from `doi->exchange_size`.
- `exchange->sa_list` temporarily owns negotiated SAs until finalization detaches them.
- `exchange->keystate` moves into `msg->isakmp_sa->keystate` during phase-1 finalization.
- Phase-1 IDs are copied between exchange and ISAKMP SA depending on which side already has them.
- `exchange->finalize` may be a composed chain built by `exchange_add_finalization()`.

Important dependencies:
- `doi_lookup()` and DOI handler callbacks: initiator/responder, scripts, finalization, free hooks.
- Message layer: allocation, replies, payload scanning, send, drop, post-send callbacks.
- SA layer: create, release/free, lookup, replacement marking.
- Config, transport, timers, KeyNote, cert/key handlers, NAT-T/DPD integrations.

Notable details:
- Exchange expiration is controlled by `General/Exchange-max-time`, defaulting to 120 seconds.
- Last messages are retained for duplicate/retransmit handling. Completed exchanges with no `last_sent` can be freed immediately.
- The finalization path starts DPD only after SAs are detached, avoiding a race with exchange cleanup.
