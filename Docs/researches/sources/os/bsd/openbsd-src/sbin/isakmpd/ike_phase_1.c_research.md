# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.c

Shared phase-1 IKE helper implementation used by Main Mode and Aggressive Mode.

Major functions:
- `ike_phase_1_initiator_send_SA()` builds the initiator SA payload from configured transforms, stores transform offers on the exchange SA, saves the SA body for HASH computation, and advertises OpenBSD, NAT-T, and DPD vendor IDs.
- `ike_phase_1_initiator_recv_SA()` validates that the responder selected exactly one SA/proposal/transform, negotiates it against offers, decodes the transform, and selects the DH group.
- `ike_phase_1_responder_recv_SA()` validates initiator proposals, negotiates an acceptable transform, decodes attributes, checks mandatory crypto/hash/auth/group state, and stores the initiator SA body.
- `ike_phase_1_responder_send_SA()` emits the selected SA and vendor payloads.
- `ike_phase_1_send_KE_NONCE()` emits DH public value, nonce, pending CERTREQ/CERT payloads, and NAT-D payloads when needed.
- `ike_phase_1_recv_KE_NONCE()` saves peer DH public value, nonce, CERTREQs, and Main Mode NAT-D checks.
- `ike_phase_1_post_exchange_KE_NONCE()` computes DH shared secret, SKEYID, SKEYID_d/a/e, derives/extends encryption key material, initializes crypto state, handles weak DES key retry, and initializes IV from hash(g_xi | g_xr).
- `ike_phase_1_send_ID()` builds the local phase-1 ID from configured ID sections or transport source address.
- `ike_phase_1_recv_ID()` validates optional configured `Remote-ID`, stores peer ID, and marks the payload.
- `ike_phase_1_send_AUTH()` delegates HASH/SIG creation to the selected auth method.
- `ike_phase_1_recv_AUTH()` delegates HASH/SIG decoding, recomputes expected HASH_I/HASH_R, compares it, and marks the message authenticated.
- `ike_phase_1_validate_prop()` and `attribute_unacceptable()` validate peer transform attributes against configured policy, including lifetimes, algorithms, group, PRF, key length, field size, and group order.

Important dependencies:
- Attribute encoding/decoding, config lists, DH groups, crypto transforms, PRF/hash/auth modules, `ipsec_exch` DOI data, NAT-T, DPD, vendor payloads, message and SA layers.

Notable behavior:
- Aggressive Mode requires consistent group descriptions across all offered transforms.
- Nonce size defaults to 16 for initiator send, while responders mirror the initiator nonce length.
- Mandatory phase-1 attributes are enforced on responder receive: crypto transform, hash, auth method, and DH group.
