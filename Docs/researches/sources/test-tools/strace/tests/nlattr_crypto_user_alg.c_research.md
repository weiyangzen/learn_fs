# sources/test-tools/strace/tests/nlattr_crypto_user_alg.c

Purpose: verifies crypto-user netlink attribute decoding for `struct crypto_user_alg` messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_CRYPTO)`, `struct crypto_user_alg`, `CRYPTOCFGA_*`, `CRYPTOCFGA_REPORT_*`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT_EX`, `check_*_nlattr` helpers, and crypto xlat constants.

Control flow: initializes a crypto-user algorithm header, prints it, then tests attributes such as priority, report type names, larval/hash/skcipher/rng reports, and object payloads with fixed strings and numeric fields.

State and persistence: all crypto algorithm data is synthetic message memory; no kernel crypto algorithm registration is modified.

Dependencies and integration points: depends on `linux/cryptouser.h`, `test_nlattr.h`, and strace crypto nlattr decoders.

Risks and edge cases: fixed-size string arrays, report type xlat values, object-size checks, and optional constants can affect expected output.

Test signals: expected output shows decoded `CRYPTOCFGA_*` attributes and structured crypto report objects with symbolic fields.
