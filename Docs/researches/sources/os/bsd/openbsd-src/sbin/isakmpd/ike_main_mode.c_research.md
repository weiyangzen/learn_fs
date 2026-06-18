# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.c

Main Mode phase-1 dispatch tables and small step wrappers. It maps the six-message Identity Protection exchange onto shared phase-1 helpers.

Initiator sequence:
- Send SA.
- Receive SA.
- Send KE/NONCE.
- Receive KE/NONCE.
- Enable encryption, send ID/AUTH, then send INITIAL-CONTACT.
- Receive ID/AUTH.

Responder sequence:
- Receive SA.
- Send SA.
- Receive KE/NONCE.
- Send KE/NONCE and register post-send DH/key-material computation.
- Receive ID/AUTH.
- Enable encryption, send ID/AUTH, then send INITIAL-CONTACT.

Notable detail:
- `responder_send_KE_NONCE()` uses the initiator nonce length for responder nonce size and computes DH/key material in a post-send callback to overlap computation with network round trip.
