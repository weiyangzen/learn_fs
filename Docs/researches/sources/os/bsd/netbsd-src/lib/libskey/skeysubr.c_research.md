# File Research: sources/os/bsd/netbsd-src/lib/libskey/skeysubr.c

## Purpose
Implements S/Key hash/key derivation, one-way key iteration, hex conversion, terminal password reading, and small string utilities.

## Main Interfaces
Exports `keycrunch`, `f`, `rip`, `readpass`, `readskey`, `atob8`, `btoa8`, `htoi`, `skipspace`, `backspace`, `sevenbit`, `skey_set_algorithm`, and `skey_get_algorithm`.

## Control Flow And State
A global `skey_hash_type` indexes an algorithm table. Supported active algorithms are MD4, MD5, and SHA1; RMD160 code is present but disabled.

`keycrunch` lowercases the seed, concatenates seed and password, masks input to seven bits, hashes it, and folds the digest to the 64-bit S/Key binary key. MD4/MD5 fold 128 bits by XORing digest halves. SHA1 folds 160 bits and manually emits little-endian bytes as required by RFC 2289.

`f` applies one in-place one-way hash iteration to an 8-byte key using the selected algorithm.

Input helpers disable terminal echo for secret password reads, restore echo on normal completion or SIGINT, strip trailing CR/LF, and seven-bit-clean input. OTP reads leave echo enabled.

Conversion helpers parse or emit 16 hex nibbles with optional whitespace on input. `backspace` removes backspaced characters from a string.

## Dependencies
Uses NetBSD MD4/MD5/SHA1/RMD160 headers, termios, signals, ctype, and public constants from `skey.h`.

## Risks And Notes
The selected hash algorithm is global process state, so concurrent users or nested calls can interfere. The terminal echo helper stores static termios state and is not reentrant. SHA1 uses internal `SHA1_CTX.state` after `SHA1Final(NULL, &sha)`, binding behavior to this SHA1 implementation.
