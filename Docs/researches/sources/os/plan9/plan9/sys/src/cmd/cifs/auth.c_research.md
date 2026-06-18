# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/auth.c

Production CIFS authentication implementation. Supports `plain`, `lm+ntlm`, `ntlm`, and default `ntlmv2`; plaintext is rejected unless explicitly selected when the server requires it.

Uses Plan 9 auth/factotum APIs for password or MS-CHAP responses. NTLMv2 derives v1 and v2 hashes, emits LMv2/NTLMv2 challenge responses, and builds MAC keys for SMB signing. `macsign(Pkt*, int)` computes or verifies the 8-byte SMB signature at SMB header offset 14, using `BSRSPYL ` before sequence running starts and the negotiated auth MAC key afterward.

Security note: comments explicitly warn LM/NTLM are weak and Kerberos would be preferred, but Kerberos is not implemented.
