# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/auth-testcase.c

Authentication test variant for CIFS. It duplicates the auth logic but enables `NTLMV2_TEST`, forcing deterministic server challenge, user/domain, timestamp, nonce, and expected debug dumps for NTLMv2 vectors.

Implements `plain`, `lm+ntlm`, `ntlm`, and `ntlmv2` methods, selected by `getauth`. It derives NTLMv2 hashes from the UTF-16LE password MD4 hash plus HMAC-MD5 over uppercased user/domain material, builds LMv2 and NTLMv2 responses, and prepares MAC keys.

The `macsign` here is diagnostic: it tries nearby sequence numbers and zero/LM/NT keys before writing a signature. It differs from production `auth.c` and appears intended as a standalone testcase/debug copy rather than the normal build path.
