# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/key.c

Key conversion helpers for passphrase and RSA key material.

It frees internal keys by type, serializes passphrases as duplicated strings and RSA keys as DER public/private blobs, renders serialized passphrases as strings and RSA blobs as hex, internalizes serialized data back into passphrase strings or OpenSSL RSA objects, and parses printable RSA hex back into serialized bytes.

Unsupported or unknown key types are logged. DSA constants exist in the header, but this implementation only handles passphrases and RSA.
