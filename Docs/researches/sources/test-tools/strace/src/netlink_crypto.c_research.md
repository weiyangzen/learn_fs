<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_crypto.c -->
# sources/test-tools/strace/src/netlink_crypto.c

Purpose: decodes `NETLINK_CRYPTO` algorithm messages and their crypto report attributes.

Important APIs/types/functions: `decode_netlink_crypto`, `decode_crypto_user_alg`, report decoders for generic/hash/blkcipher/aead/rng/cipher payloads, and `crypto_user_alg_nla_decoders`.

Control flow: supported crypto message types (`NEWALG`, `DELALG`, `UPDATEALG`, `GETALG`) decode a leading `struct crypto_user_alg`; if aligned trailing data exists, `decode_nlattr` decodes `CRYPTOCFGA_*` attributes using report-specific structure printers.

State and persistence behavior: no persistent state. It copies tracee netlink payload structures and prints fields or raw short strings for undersized reports.

Dependencies and integration points: depends on `netlink.h`, `nlattr.h`, `<linux/cryptouser.h>`, `xlat/crypto_nl_attrs.h`, and the main `netlink.c` family dispatch.

Risks: crypto report structures evolve with kernel headers; short payloads intentionally fall back to string/hex output. C string fields rely on kernel-provided fixed buffers being printable.

Test signals: trace crypto algorithm dumps containing priority, hash, cipher, AEAD, RNG, generic report attributes, short attributes, unknown attributes, and all four supported crypto message types.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_crypto.c -->
