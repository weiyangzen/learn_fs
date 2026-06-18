# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap.c

`snoopy` Extensible Authentication Protocol decoder.

Key behavior:
- Parses EAP code, id, length, and optional request/response type.
- Demuxes request/response subtypes to identity, notify, nak, MD5, OTP, GTC, TTLS, expanded, or experimental handlers.
- Formats EAP operation name, id, type, and length.
- Implements `eap_identity` pseudo-protocol formatter for identity/prompt/options payloads.

Integration:
- Reached from `eapol.c`.
- `eap_identity.c` is only a placeholder; real symbol lives here.

Risks and notes:
- Context is lost for identity request vs response, so identity payloads are interpreted uniformly.
