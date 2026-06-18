# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.c

Aggressive Mode phase-1 dispatch tables and step wrappers. It composes shared `ike_phase_1_*` helpers into the three-message aggressive exchange.

Initiator steps:
- Send SA, KE, NONCE, ID.
- Receive selected SA, KE, NONCE, ID, AUTH.
- Enable encryption and send AUTH.

Responder steps:
- Receive SA, ID, KE, NONCE.
- Send selected SA, KE, NONCE, ID, AUTH.
- Receive AUTH and, if peer is NAT-T capable, check NAT-D payloads.

Notable behavior:
- The initiator does not send INITIAL-CONTACT in Aggressive Mode, with comments explaining RFC conflict/interop concerns.
- `responder_send_SA_KE_NONCE_ID_AUTH()` performs post-DH/key-material computation before sending responder ID/AUTH.
