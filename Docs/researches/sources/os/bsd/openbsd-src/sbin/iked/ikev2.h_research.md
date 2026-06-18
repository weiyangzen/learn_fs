# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2.h

## Role

`ikev2.h` is the IKEv2 protocol definition header used by OpenBSD `iked`. It defines wire-format packed structures, protocol constants, notification numbers, transform IDs, state IDs, payload IDs, configuration-payload attributes, and external lookup-map declarations used for parsing, construction, logging, and policy matching.

## State and Header Constants

The file defines IKE version constants and the IKEv2 key pad string used for PSK AUTH derivation. It enumerates internal pseudo-states from initial SA creation through cookie handling, SA_INIT, EAP, AUTH, validation, established, closing, and closed states.

It also defines IKEv2 exchange types, IKE header flags, and external `iked_constmap` declarations for printing or mapping states, exchanges, and flags.

## Wire Payload Structures

All protocol structures are marked `__packed`, reflecting direct wire-layout use:

- `struct ikev2_payload`: generic payload header with next-payload, reserved/critical-bit byte, and length.
- `struct ikev2_frag_payload`: RFC7383 encrypted fragment numbering.
- `struct ikev2_sa_proposal`: SA proposal header followed by SPI and transforms.
- `struct ikev2_transform`: transform header followed by transform attributes.
- `struct ikev2_attribute`: transform attribute header.
- `struct ikev2_keyexchange`: KE payload DH group header.
- `struct ikev2_notify`: notify payload header.
- `struct ikev2_delete`: delete payload header.
- `struct ikev2_id`: ID payload header.
- `struct ikev2_cert`: CERT/CERTREQ encoding byte.
- `struct ikev2_tsp` and `struct ikev2_ts`: traffic selector payload structures.
- `struct ikev2_auth`: AUTH payload method header.
- `struct ikev2_cp` and `struct ikev2_cfg`: configuration payload and attribute headers.

## Protocol Registries

The header captures IANA/RFC IKEv2 registry values for payload types, SA protocol IDs, transform types, encryption transforms, PRFs, integrity/auth transforms, DH groups, ESN, attribute types, notify types, ID types, certificate encodings, traffic selector types, AUTH methods, signature hash algorithms, CP message types, and CP attribute types.

It includes common modern algorithms such as AES-CBC/CTR/GCM/CCM, ChaCha20-Poly1305, SHA2 PRFs and integrity algorithms, ECP groups, Curve25519, and an OpenBSD private hybrid `X_SNTRUP761X25519` DH group value.

## Internal and Private Values

Several values are explicitly internal or private to `iked`:

- AEAD auth placeholders `IKEV2_XFORMAUTH_AES_GCM_8/12/16`.
- `IKEV2_AUTH_SIG_ANY`, an internal policy value that accepts multiple signature AUTH methods.
- `IKEV2_CERT_ECDSA` and `IKEV2_CERT_BUNDLE` private certificate encodings.
- `IKEV2_SAPROTO_IPCOMP` as a private workaround value.
- Fragment size calculations for IPv4 and IPv6 IKE packets.
- `IKEV2_MAXNUM_TSS` for the 8-bit traffic-selector count field.

## Configuration Payload Coverage

The CP section defines request/reply/set/ack values and attributes for internal IPv4/IPv6 address assignment, DNS/NBNS/DHCP/server attributes, subnets, application version, supported attributes, and Microsoft private server attributes. These constants are used by `ikev2.c` to request, assign, and reply with virtual/internal addresses and DNS data.

## IKEv1 Compatibility Constants

At the end, the header defines minimal IKEv1 payload constants used by the IKEv2 proposal builder for proposal chaining fields: `IKEV1_PAYLOAD_NONE` and `IKEV1_PAYLOAD_PROPOSAL`.

## Research Notes

This header is foundational for the parser and builder code: any numeric change affects on-wire interoperability. The packed structs are intentionally minimal and often followed by variable-length data, so users must pair them with explicit bounds checking and endian conversion in implementation code.
