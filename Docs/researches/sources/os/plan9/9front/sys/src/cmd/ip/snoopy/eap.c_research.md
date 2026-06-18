# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap.c

This module decodes Extensible Authentication Protocol packets and includes the `eap_identity` sub-protocol implementation.

The EAP header contains code, id, length, and optional type for Request/Response. The mux table maps Identity, Notify, Nak, MD5, OTP, GTC, TTLS, expanded, and experimental types.

`p_filter` validates/truncates to the EAP length, advances past the EAP header and type byte for Request/Response packets, and matches selected type. `p_seprint` prints id, code name, type name when present, and length, then demuxes the remaining body.

`p_seprintidentity` prints EAP Identity data. It has special handling for a NUL-separated prompt/options layout; otherwise it prints the remaining bytes as text.

The file registers both `Proto eap` and `Proto eap_identity`.
