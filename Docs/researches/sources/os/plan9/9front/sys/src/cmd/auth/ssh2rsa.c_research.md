# File Research: sources/os/plan9/9front/sys/src/cmd/auth/ssh2rsa.c

Converter from OpenSSH private key format `openssh-key-v1` to Plan 9 factotum RSA key format.

Important behavior:
- Reads key from stdin or one file.
- Validates OpenSSH magic.
- `decode()` skips cipher/kdf fields, reads number of keys, public key blob, and private key blob.
- `fill()` only accepts RSA keys. It parses public exponent and modulus from public blob, verifies private check integers match, rejects encrypted private keys, skips repeated public values and comment/iq, reads private exponent and primes, then calls `rsafill()`.
- Outputs a factotum-style key line containing `service=ssh proto=rsa`, key size, public exponent, private exponent, modulus, primes, and CRT values.

Risks/notes:
- Encrypted OpenSSH private keys are reported as “private key seems encrypted” and unsupported.
- Parser is strict about blob boundaries and component lengths.
