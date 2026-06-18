# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.c

Implements IKE Quick Mode phase-2 negotiation for IPsec SAs.

Dispatch:
- Initiator steps: send HASH/SA/NONCE, receive HASH/SA/NONCE, send final HASH.
- Responder steps: receive HASH/SA/NONCE, send HASH/SA/NONCE, receive final HASH.

Major behavior:
- `check_policy()` integrates KeyNote policy checks for negotiated phase-2 SAs and IDs. It builds principals from PSKs, KeyNote certs, or X.509/RSA certs and queries policy with true/false return values. If policy is disabled or ignored, it allows the negotiation.
- `initiator_send_HASH_SA_NONCE()` builds SA proposals from configured suites/protocols/transforms, allocates incoming SPIs through the DOI, stores local offer state in `proto`/`proto_attr`, handles NAT-T encapsulation mapping for ESP, sends nonce, optional PFS KE, optional client IDs, and fills HASH(1).
- `initiator_recv_HASH_SA_NONCE()` verifies HASH(2), authenticates the message, parses/synthesizes client IDs, records chosen transforms, prunes unchosen offers, enforces policy, saves responder nonce, and handles optional PFS KE.
- `initiator_send_HASH()` emits HASH(3), registers optional PFS shared-secret generation and Quick Mode post-processing.
- `responder_recv_HASH_SA_NONCE()` verifies HASH(1), authenticates the message, parses/synthesizes IDs, negotiates an acceptable SA under policy, validates AH/auth and PFS group consistency, saves nonce/KE, and assigns a passive connection name by IDs.
- `responder_send_HASH_SA_NONCE()` emits HASH(2), selected SA payloads, nonce, optional PFS KE, mirrored client IDs, and registers optional PFS shared-secret generation.
- `responder_recv_HASH()` verifies HASH(3), authenticates the message, and runs `post_quick_mode()`.
- `post_quick_mode()` derives inbound and outbound KEYMAT for each non-IPComp negotiated protocol using SKEYID_d, optional PFS g^xy, protocol ID, SPI, and both nonces; then logs Quick Mode completion.
- `gen_g_xy()` computes optional PFS DH shared secret after KE exchange.

Important dependencies:
- ISAKMP SA phase-1 key material from `msg->isakmp_sa->data`.
- PRF/hash layer, DOI SPI/proto hooks, message SA negotiation, IPsec transform decoding, connection lookup, policy/KeyNote, cert/key helpers.
- Transport endpoints for implicit Quick Mode IDs when IDci/IDcr are omitted.

Notable constraints:
- Current initiator receive path says multiple SA payloads in Quick Mode are unsupported.
- Client ID support is limited to IPv4/IPv6 address/subnet and FQDN in NAT-T transport-mode cases.
- PFS group descriptions must be consistent across accepted SAs.
