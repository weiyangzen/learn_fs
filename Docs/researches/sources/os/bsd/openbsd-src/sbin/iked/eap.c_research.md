# File Research: sources/os/bsd/openbsd-src/sbin/iked/eap.c

`eap.c` implements IKEv2 EAP message construction and parsing, with direct support for EAP Identity and EAP-MSCHAPv2 plus pass-through behavior for RADIUS-backed EAP.

Responder-side flows include sending IDr/CERT/AUTH/EAP identity requests, generating MSCHAPv2 challenges, sending success/failure-style EAP messages, and parsing MSCHAPv2 responses into `msg_parent->msg_eap` for parent/RADIUS/user verification.

`eap_parse()` validates EAP header lengths, handles request/response/success/failure codes, extracts identities, logs/parses MSCHAPv2 challenge/response/success/failure payloads, and dispatches to `eap_mschap()` when local MSCHAPv2 handling is needed. Unsupported EAP types are accepted only when policy auth is `EAP_TYPE_RADIUS`.

Security-relevant details: variable strings are parsed through `get_string()`, short protocol messages are rejected, responder-only MSCHAPv2 is enforced, duplicate identity handling avoids replacing an existing SA identity, and challenge values are randomly generated and stored in SA EAP state.
