# File Research: sources/os/bsd/netbsd-src/lib/libskey/skeylogin.c

## Purpose
Implements S/Key challenge lookup, response verification, authentication prompting, keyfile iteration, and key disabling.

## Main Interfaces
Exports `getskeyprompt`, `skeychallenge`, `skeylookup`, `skeygetnext`, `skeyverify`, `skey_haskey`, `skey_keyinfo`, `skey_passcheck`, `skey_authenticate`, and `skeyzero`.

## Control Flow And State
`openSkey` opens `_PATH_SKEYKEYS` read/write if present and forces mode `0600`. Lookup scans records, skipping comments, parsing optional hash algorithm, sequence, seed, and value, then seeks back to the matching record start. If no algorithm is present, MD4 is assumed.

Challenge helpers format `otp-<algorithm> <sequence-1> <seed>` using bounded hash and seed widths. `getskeyprompt` also strips high bits from the username before lookup.

`skeyverify` converts a response from English words or hex to an 8-byte key, applies one hash iteration, locks the keyfile with `flock`, rereads the original record to avoid stale challenge reuse, compares against the stored key, then rewrites the same record with the new key and decremented sequence number. MD4 records omit the algorithm name to preserve legacy fixed record length; other algorithms include it.

`skey_authenticate` prints a challenge, reads a response, verifies it, warns when fewer than five logins remain, and returns success/failure. Optional fake-challenge code can synthesize prompts for nonexistent users when compiled in. `skeyzero` comments out the current keyfile record by writing `#` at its start.

## Dependencies
Uses key conversion/hash helpers from `skeysubr.c` and `put.c`, `_PATH_SKEYKEYS`, `flock`, stdio file positioning, local time formatting, optional SHA1 fake-challenge support, and terminal input helpers.

## Risks And Notes
Correctness depends on rewriting records without changing their effective fixed-width layout. The keyfile lock is acquired only during verification/update, so lookup data must be reread after locking. Some error paths close `keyfile`, but lock-failure returns without closing it. The code uses legacy MD4 by default unless records specify another supported algorithm.
