# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2_pld.c

Read completely: 2213 lines.

Implements IKEv2 payload parsing and validation for iked. It walks the payload chain, bounds-checks every generic/substructure header before copying, parses encrypted SK/SKF payloads recursively, reassembles encrypted fragments, records peer-provided message state into the parent `iked_message`, and handles SA, transform, KE, ID, certificate, AUTH, nonce, notify, delete, traffic-selector, configuration, and EAP payloads.

Top-level parser:
- `ikev2_pld_parse()` logs the IKE header, verifies the datagram contains `ike_length`, advances past the IKE header, and calls `ikev2_pld_payloads()`.
- `ikev2_validate_pld()` checks the generic payload header exists, verifies declared length fits in remaining bytes, and rejects payloads shorter than the generic header.
- `ikev2_pld_payloads()` iterates the payload chain, marks decrypted recursion with `IKED_E`, dispatches by payload type plus decrypted state, sends an informational response on parse errors from peer messages, and enforces SK/SKF as terminal payloads.

SA proposals and transforms:
- `ikev2_validate_sa()` verifies proposal substructure minimum size, declared length, single/multiple proposal consistency, and remaining length.
- `ikev2_pld_sa()` parses proposal headers, optional 4- or 8-byte SPI, creates peer proposals with `config_add_proposal()` only for peer-originated messages, stores peer/local SPI metadata, parses transforms, and drops invalid peer proposal transforms while keeping the rest of the SA payload parseable.
- `ikev2_validate_xform()` and `ikev2_pld_xform()` parse transform headers, log transform IDs using type-specific maps, parse transform attributes, add transforms to the current peer proposal, recursively continue through `IKEV2_XFORM_MORE`, and reject trailing bytes after the final transform.
- `ikev2_validate_attr()` and `ikev2_pld_attr()` parse TV/TLV attributes, record `KEY_LENGTH` into `msg_attrlength`, validate TLV lengths, print TLV data, and recursively consume multiple attributes.

Identity, key exchange, certificates, and auth:
- `ikev2_validate_ke()` and `ikev2_pld_ke()` parse DH group and KE data, reject empty KE payloads, reject duplicate peer KE, and save `msg_ke` plus `msg_dhgroup`.
- `ikev2_validate_id()` rejects missing/invalid ID headers and `IKEV2_ID_NONE`; `ikev2_pld_id()` stores the full ID payload including header into the expected peer/local ID slot based on SA role and IDi/IDr payload type, rejecting duplicates and malformed printable IDs.
- `ikev2_validate_cert()` rejects absent/invalid certificate type; `ikev2_pld_cert()` ignores local-generated parse state, rejects internal `IKEV2_CERT_BUNDLE` on the wire, stores the first peer cert in `msg_cert`, and stores supplemental certs up to `IKED_SCERT_MAX`.
- `ikev2_validate_certreq()` and `ikev2_pld_certreq()` parse cert requests, validate X.509 request data as SHA1-hash multiples when present, and append peer certreq records to `msg_certreqs`.
- `ikev2_validate_auth()` rejects missing auth headers and method zero; `ikev2_pld_auth()` stores the peer AUTH data/method and rejects duplicate AUTH payloads.
- `ikev2_pld_nonce()` rejects empty nonces, rejects duplicate peer nonce, and saves the nonce to the parent.

Notify/delete/traffic selectors:
- `ikev2_validate_notify()` and `ikev2_pld_notify()` parse notify headers and implement state updates for NAT detection, authentication failure, invalid KE, no additional SAs, rekey SA, temporary failure, IPCOMP support, child SA not found, no proposal chosen, MOBIKE support, transport mode, update SA addresses, COOKIE2, COOKIE, fragmentation support, and signature hash algorithms.
- Notify handling enforces encryption requirements for sensitive post-auth notifications and rejects/ignores malformed length combinations depending on notification semantics.
- `ikev2_validate_delete()` and `ikev2_pld_delete()` parse DELETE payloads, ignore response deletes from peers, reject duplicate delete payloads, validate SPI list length/count, and save delete SPI metadata and buffer.
- `ikev2_validate_tss()`, `ikev2_pld_tss()`, `ikev2_validate_ts()`, and `ikev2_pld_ts()` parse TSi/TSr lists, validate individual selector lengths, log IPv4/IPv6 ranges, ignore unknown selector types, and reject leftover bytes after address ranges.

Encrypted payloads and fragmentation:
- `ikev2_validate_ef()` and `ikev2_pld_ef()` parse SKF fragment headers, limit total fragments to `IKED_FRAG_TOTAL_MAX`, reject zero or out-of-range fragment numbers, decrypt each fragment, allocate the SA fragment array on first fragment, reject total-count changes, drop duplicates, remember the first fragment's next-payload value, and trigger reassembly once all fragments arrive.
- `ikev2_frags_reassemble()` concatenates plaintext fragments in order, flushes original request retransmits for response-side reassembly, creates a decrypted child message, parses the reassembled plaintext payload chain, updates reassembly/drop counters, and frees stored fragments.
- `ikev2_pld_e()` rejects receiving a normal SK while SKF fragments are queued, decrypts the SK payload, flips SA initiator direction temporarily for locally generated parse cases, and recursively parses decrypted payloads.

Configuration and EAP:
- `ikev2_validate_cp()` and `ikev2_pld_cp()` parse configuration payloads and attributes, validate cfg lengths, store one IPv4 address, IPv6 address, or DNS address from peer replies/requests, and record the CP type on the parent.
- `ikev2_validate_eap()` and `ikev2_pld_eap()` validate EAP header/payload length, log code/id/type, call `eap_parse()`, reject duplicate EAP payloads, store the raw EAP message, and mark EAP found.
- `ikev2_pld_parse_quick()` is a lightweight parser for initial/retransmitted payloads that does not require `msg_sa`; it primarily extracts SKF fragment number for retransmit response logic.

Risks and notes:
- The parser deliberately mutates only peer-originated messages in most handlers, using `ikev2_msg_frompeer()` as the guard.
- Multiple handlers accept malformed optional notifications by ignoring them rather than failing the whole message, while core structural errors fail.
- Fragment reassembly assumes every fragment slot is populated before concatenation and uses `fatalx()` if that invariant is violated.
- Several TODO/XXX comments note limited support for multiple CP values and future improvements around flow or payload semantics.
