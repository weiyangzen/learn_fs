# sources/user-network-fs/impacket/tests/SMB_RPC/test_ntlm.py

## Purpose

`test_ntlm.py` is a local protocol-vector suite for Impacket's NTLM implementation. It checks NTLMv1, NTLMv1 with extended session security, NTLMv2, message sealing/signing, authenticate-message packing, AV pair container behavior, and negotiate-message version-field packing.

## Important APIs, Types, and Functions

The only class is `NTLMTests(unittest.TestCase)`. `setUp()` enables `ntlm.TEST_CASE`, fixes deterministic user/domain/password/server/workstation values, session keys, timestamp, client and server challenges, negotiate flags, sequence number, nonce, and UTF-16LE plaintext.

The tests exercise `LMOWFv1`, `NTOWFv1`, `NTOWFv2`, `computeResponseNTLMv1`, `computeResponseNTLMv2`, `KXKEY`, `generateEncryptedSessionKey`, `NTLMAuthChallengeResponse`, `SIGNKEY`, `SEALKEY`, `SEAL`, `AV_PAIRS`, `NTLMAuthNegotiate`, and `VERSION`. `Cryptodome.Cipher.ARC4` is used to reproduce RC4 sealing behavior.

## Control Flow

`test_ntlmv1` disables NTLMv2 and follows Microsoft-style examples: derive LM and NT one-way functions, compute NTLMv1 responses and session base keys, derive key-exchange keys, encrypt a deterministic exported session key, pack an authenticate message, and seal/sign a UTF-16LE plaintext. It then repeats a branch with extended session security and client challenge. Several known-vector assertions are active, while some TODO assertions remain commented out for cases that were not matching expected vectors.

`test_ntlmv2` enables NTLMv2, builds target-info AV bytes for domain and server names, computes NTOWFv2/LMOWFv2, responses, session base key, encrypted session key, authenticate message, signing and sealing keys, sealed payload, and signature. `test_av_pairs_container_protocol` verifies dictionary-like membership and iteration for `AV_PAIRS`. `test_refactor_negotiate_message` packs and parses negotiate messages without and with `os_version`, asserts the version flag behavior, and ensures setting `NTLMSSP_NEGOTIATE_VERSION` without an `os_version` raises.

## State and Persistence Behavior

The test intentionally mutates module globals `ntlm.TEST_CASE` and `ntlm.USE_NTLMv2`, so test isolation depends on `setUp()` resetting the deterministic mode and each method setting NTLMv1/v2 mode explicitly. There is no filesystem or network persistence. RC4 cipher instances are local and stateful for each sealing operation.

## Dependencies and Integration Points

This file sits directly on top of `impacket.ntlm` and indirectly validates behavior consumed by SMB, SPNEGO, DCERPC authentication, and secretsdump. It depends on `six.b` for byte compatibility, `struct` for flag display, and PyCryptodome's ARC4 cipher. The expected values are protocol-vector integration points for cryptographic compatibility.

## Risks and Edge Cases

Because this file manipulates NTLM global flags, failures or future parallelization could leak mode into other tests if not isolated by the runner. Some TODO vectors remain commented, which means those code paths are executed and printed but not fully verified. Deterministic test-case mode suppresses time/random variation and is essential for reproducible NTLMv2 output. The negotiate-message tests protect a subtle refactor risk: emitting the version flag without version bytes creates malformed messages.

## Test Signals

High-value signals are exact known-vector matches for one-way functions, response blobs, session keys, authenticate messages, signing/sealing keys, sealed data, and signatures. The file should be run after changes to NTLM crypto, flag handling, AV pairs, message layout calculations, SPNEGO integration, or SMB/DCERPC authentication code.
