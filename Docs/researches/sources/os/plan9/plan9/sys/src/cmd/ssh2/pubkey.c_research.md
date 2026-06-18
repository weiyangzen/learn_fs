# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/pubkey.c

This file reads, matches, appends, and replaces RSA public keys in Plan 9 SSH keyring files.

Key behavior:
- Parses public key lines with optional host alias prefix and RSA exponent/modulus in decimal or hexadecimal.
- Reads keys from a `Biobuf`, skipping comments and warning on unparsable lines.
- Matches comma-separated host aliases against a requested host.
- Finds whether a host key is absent, present and matching, or present but different.
- Appends new keys or rewrites a keyring via a `.new` file and `dirwstat` rename.

Important details:
- `Arbsz` is a minimum-size sanity check for RSA modulus/key sizes.
- Replacing a key removes every matching alias entry and appends the new key.
- Key output uses Plan 9 mp formatting with truncated display precision (`%.10M`).

Filesystem relevance:
- Direct: manages user/system keyring files such as `/sys/lib/ssh/keyring` and `$home/lib/keyring`.
