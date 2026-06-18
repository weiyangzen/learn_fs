# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.h

Defines `struct exchange`, exchange flags, timeout constant, and the public exchange API.

Core fields:
- Hash/list ownership: `link`, `linked`.
- Naming/policy: `name`, `policy`, `policy_id`.
- Finalization hook and argument.
- Temporary negotiated SAs in `sa_list`.
- Lifetime timer `death`.
- ISAKMP cookies, phase-2 `message_id`, exchange `type`, `phase`, `step`, `initiator`.
- Flags for commit, encryption, NAT-T, DPD, peer type.
- DOI pointer and DOI-specific `data`.
- Script program counter `exch_pc`.
- Retransmit/duplicate state: `last_received`, `last_sent`, `in_transit`.
- Nonces and IDs for initiator/responder.
- Crypto state: transform, key length, keystate.
- Authentication/cert/key material used by policy and kernel export.
- CERTREQ acceptable CA list.

Exports lifecycle, lookup, establishment, nonce/cert helpers, script lookup, setup, run, finalize, and phase-1 cookie upgrade functions.

Notable flags:
- `EXCHANGE_FLAG_ENCRYPT` gates encrypted exchange handling.
- `EXCHANGE_FLAG_NAT_T_*` records NAT traversal negotiation details.
- `EXCHANGE_FLAG_DPD_CAP_PEER` records DPD peer capability.
