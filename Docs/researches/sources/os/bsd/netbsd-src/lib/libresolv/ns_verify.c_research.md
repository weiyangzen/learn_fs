# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_verify.c

Read completely: 485 lines.

Implements TSIG discovery and verification. `ns_find_tsig()` walks the DNS message sections and returns the final additional record only if it is a TSIG. `ns_verify()` parses that record, validates HMAC-MD5 algorithm/key identity, recomputes the MAC over the same canonical fields used by `ns_sign()`, optionally returns the signature, and strips the TSIG from the message unless `nostrip` is set.

Time validation compares the signed time to the local clock within the advertised fudge window. The function distinguishes format errors, missing TSIG, BADKEY, BADSIG, BADTIME, and server-returned TSIG errors.

TCP verification keeps rolling state in `ns_tcp_tsig_state`, accepts unsigned intermediate messages when TSIG is not required, and verifies signed checkpoints/final messages by including the previous signature and current message prefix.
