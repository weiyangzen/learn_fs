# sources/user-network-fs/impacket/impacket/ntlm.py

## Purpose
`ntlm.py` implements Impacket's NTLMSSP message model, NTLMv1/NTLMv2 response generation, session key derivation, signing/sealing helpers, and small HTTP wrapper classes for NTLM authorization headers. It is the shared authentication primitive used by SMB, relay clients, DCE/RPC transports, HTTP authentication, LDAP relay paths, and other protocol modules that need to build or parse NTLM type 1, type 2, and type 3 messages.

## Important APIs, Types, and Functions
The module-level constants define NTLMSSP negotiation flags, auth levels, message types, and AV pair identifiers. `USE_NTLMv2` globally defaults high-level helpers to NTLMv2 unless overridden, while `TEST_CASE` disables normal timestamp/SPN AV-pair mutation for deterministic tests.

`AV_PAIRS` parses and serializes NTLM target-info AV pairs as a dictionary of `type -> (length, bytes)` entries. `VERSION`, `NTLMAuthNegotiate`, `NTLMAuthChallenge`, and `NTLMAuthChallengeResponse` are `Structure` subclasses for the wire-level NTLMSSP messages. `NTLMMessageSignature` selects extended or legacy signature layouts through `ExtendedOrNotMessageSignature`.

The high-level entry points are `getNTLMSSPType1()` and `getNTLMSSPType3()`. `computeResponse()` dispatches to `computeResponseNTLMv1()` or `computeResponseNTLMv2()`. Hash and response helpers include `compute_lmhash()`, `compute_nthash()`, `NTOWFv1()`, `LMOWFv1()`, `NTOWFv2()`, `LMOWFv2()`, `get_ntlmv1_response()`, and the DES internals `__expand_DES_key()`, `__DES_block()`, and `ntlmssp_DES_encrypt()`. Session-security helpers include `KXKEY()`, `generateEncryptedSessionKey()`, `SIGNKEY()`, `SEALKEY()`, `MAC()`, `SIGN()`, and `SEAL()`. `NTLM_HTTP`, `NTLM_HTTP_AuthRequired`, `NTLM_HTTP_AuthNegotiate`, and `NTLM_HTTP_AuthChallengeResponse` provide minimal HTTP header token parsing/typing.

## Control Flow
For a normal NTLMSSP exchange, callers create a type 1 message with `getNTLMSSPType1()`, optionally setting signing-required flags and version bytes. The type 1 object records the workstation separately so it can later be encoded into the type 3 message without emitting workstation/domain fields in the initial negotiate message.

After a server type 2 challenge is received, `getNTLMSSPType3()` parses it as `NTLMAuthChallenge`, starts with the client's original type 1 flags, computes a random 8-byte client challenge, dispatches to `computeResponse()`, then removes response flags not echoed by the server. It derives the key-exchange key with `KXKEY()`, generates a random exported session key when key exchange is negotiated, RC4-encrypts it into `session_key`, and fills `NTLMAuthChallengeResponse` with UTF-16LE domain, user, workstation, LM response, NT response, optional version, and optional encrypted random session key. It returns both the type 3 structure and the exported session key used by protocols such as SMB signing.

The NTLMv1 path computes LM/NT one-way functions, then chooses plain NTLMv1, LM-key mode, or extended-session-security response construction based on flags. The NTLMv2 path parses server target info into `AV_PAIRS`, injects `MsvAvTargetName` as `service/<dns-hostname>` and a timestamp unless `TEST_CASE` is set, optionally adds channel bindings, builds the NTLMv2 blob, computes `ntProofStr`, LMv2 response, and session base key. Anonymous authentication special-cases blank responses and a zero key-exchange key.

Signing and sealing flow derives directional signing/sealing keys from the exported session key, computes HMAC-MD5 or legacy CRC/RC4 signatures in `MAC()`, and optionally encrypts payload bytes through a caller-provided RC4 handle in `SEAL()`.

## State and Persistence Behavior
The module has only in-process global state: `USE_NTLMv2` controls default behavior, and `TEST_CASE` changes NTLMv2 AV-pair construction. NTLM message instances store parsed byte slices and computed offsets in `Structure` fields; no filesystem or network persistence occurs. Random client challenges and exported session keys are generated with Python `random.choice()` over alphanumeric characters, so generated authentication material is process-local and not replay-stable.

## Dependencies and Integration Points
The module depends on `Cryptodome.Cipher.ARC4`, `Cryptodome.Cipher.DES`, and `Cryptodome.Hash.MD4` for core crypto, plus `hashlib`, `hmac`, `calendar`, `time`, `struct`, `base64`, and Impacket `Structure`/`LOG`. It is integrated by `smb.py` for SMB1 NTLM login and signing, by SMB2/SMB3 code for modern dialects, by relay clients for token rewriting and validation, by DCE/RPC transports for auth trailers, and by HTTP/LDAP/SMTP/IMAP/MSSQL relay modules for SPNEGO- or header-carried NTLM tokens.

## Risks and Edge Cases
Crypto imports are caught broadly and only logged; later use of `DES`, `ARC4`, or `MD4` will fail if pycryptodomex is unavailable. `AV_PAIRS.fromString()` loops until EOL without explicit bounds checks, so malformed target-info bytes can raise struct/index errors or parse unexpected fields. `AV_PAIRS.__str__()` returns an integer length instead of a string, which is surprising if used directly.

Several comparisons use identity against integer constants (`is not`) rather than value inequality; it often works for small interned integers but is semantically fragile. `getNTLMSSPType3()` uses non-cryptographic `random.choice()` for challenges/session keys. `compute_lmhash()` returns the default LM hash for non-Latin-1 passwords, which is intentional compatibility behavior but weakens LM semantics. NTLMv2 AV-pair injection assumes `NTLMSSP_AV_DNS_HOSTNAME` exists when not in test mode. `NTLMAuthChallengeResponse.checkMIC()` uses the version flag as a proxy for MIC presence, and the comment explicitly says a proper MIC check is still needed.

## Test Signals
Useful tests should cover type 1 flag construction with and without signing and version bytes, type 2 parsing with and without version/target-info fields, NTLMv1 plain/ESS/LM-key branches, NTLMv2 AV-pair injection, timestamp fallback, channel binding insertion, anonymous authentication, hash-supplied authentication, key-exchange and no-key-exchange paths, signing/sealing sequence behavior, HTTP base64 token classification, and malformed/truncated AV-pair input. Regression tests should pin known NTLMv1/NTLMv2 vectors with `TEST_CASE = True` and exercise missing pycryptodomex behavior separately.
