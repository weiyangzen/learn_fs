# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/sra.c

## Purpose
Implements Telnet SRA secure remote authentication using a public-key exchange, DES-protected username/password exchange, and PAM or password-file verification.

## Main Interfaces
Exports `sra_init`, `sra_send`, `sra_is`, `sra_reply`, `sra_status`, and `sra_printsub` when `SRA` and `ENCRYPTION` are enabled.

## Control Flow And State
Global buffers store local public/secret keys, peer public key, plaintext/encrypted username/password, password prompts, DES common key, IDEA key, and SRA validity state.

`sra_init` sets TELQUAL direction by role, allocates fixed-size buffers, resets password state, and generates a public/secret key pair. Client `sra_send` starts negotiation by sending its public key.

Server `sra_is` handles client suboptions. On `SRA_KEY`, it replies with the server public key, stores the client public key, and derives the common key. On `SRA_USER`, it decrypts the username, records it, optionally primes PAM to obtain a password prompt, encrypts the prompt, and sends `SRA_CONTINUE`. On `SRA_PASS`, it decrypts the password, checks it via PAM or fallback password validation, accepts and installs a DES session key on success, or sends another encrypted prompt on failure.

Client `sra_reply` derives the common key after receiving server public key, prompts for username, encrypts and sends it, decrypts password prompts, reads password without echo through `telnet_gets`, sends encrypted password, retries username after failed password, and installs the DES session key on accept.

PAM support uses a custom conversation that supplies already-collected username/password and captures password prompt text. Without PAM, fallback validation checks secure root terminal policy, password database lookup, shell presence, and `crypt`.

## Dependencies
Depends on telnet auth/encrypt/misc layers, `pk.c` helpers, DES session-key integration, PAM or password database/tty security APIs, `telnet_gets`, and global terminal line name.

## Risks And Notes
SRA uses legacy 192-bit DH-like exchange plus DES and should be considered historical. Global buffers make it non-reentrant. The server keeps prompting after failed password attempts without an obvious local retry limit. PAM can rewrite the username to a template user, and the code updates libtelnet state after successful authentication.
