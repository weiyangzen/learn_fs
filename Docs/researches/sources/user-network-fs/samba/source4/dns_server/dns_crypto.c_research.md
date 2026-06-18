# sources/user-network-fs/samba/source4/dns_server/dns_crypto.c

## Purpose
Handles TSIG verification and signing for Samba's internal DNS server, using GSS-TSIG/TKEY state stored in `dns_server_tkey` objects.

## Important APIs, types, and functions
- `dns_find_tkey()` searches the circular TKEY store by DNS key name using Samba DNS name equality.
- `dns_verify_tsig()` validates an incoming TSIG additional record and marks the request state authenticated.
- `dns_tsig_compute_mac()` builds the RFC TSIG signing buffer and calls `gensec_sign_packet()`.
- `dns_sign_tsig()` appends a TSIG record to an outgoing packet, including MAC data when there is no TSIG error.
- `dns_copy_tsig()` deep-copies TSIG record fields between `dns_res_rec` structures.

## Control flow
Verification finds a TSIG in the additional section, enforces that it is last, copies it into request state, removes it from the packet's additional count, finds the negotiated TKEY, checks the algorithm (`gss-tsig` or `gss.microsoft.com`), reconstructs the signed data by combining the original packet without TSIG and a fake TSIG record, decrements ARCOUNT in the raw packet bytes, and calls `gensec_check_packet()`. Access denied maps to BADSIG/REFUSED; success marks the request authenticated.

Signing creates a response TSIG. If no TSIG error is pending, it finds the TKEY, computes the MAC over optional request MAC, outgoing packet bytes, and fake TSIG data, then appends a real TSIG additional record to the packet. For `gss-tsig`, the request MAC length prefix is included; for Microsoft compatibility it is omitted.

## State and persistence behavior
No persistent storage is written. The code mutates `dns_request_state` (`sign`, `tsig`, `key_name`, `tsig_error`, `authenticated`) and the outgoing packet's additional records. TKEY state comes from the DNS server's in-memory circular store.

## Dependencies and integration points
Depends on generated DNS NDR encoders, GENSEC packet signing/checking, DNS request/server structures from `dns_server.h`, byte-order helpers, and WERROR/NTSTATUS conversion. It pairs with `dns_query.c` TKEY creation/acceptance.

## Risks and edge cases
- Time/fudge fields are copied into the MAC input, but there is no visible freshness check in this file.
- `dns_find_tkey()` assumes a valid store with `TKEY_BUFFER_SIZE` entries and scans modulo the fixed constant.
- The function mutates `packet->arcount` during verification, so later code sees TSIG removed.
- TSIG must be last; otherwise the request fails format validation.
- Algorithm string handling is exact and supports only two names.

## Test signals
Important tests include valid GSS-TSIG verification, BADKEY, BADSIG, TSIG-not-last format error, response signing with and without request MAC, both algorithm names, and interaction with TKEY negotiation in `dns_query.c`.
