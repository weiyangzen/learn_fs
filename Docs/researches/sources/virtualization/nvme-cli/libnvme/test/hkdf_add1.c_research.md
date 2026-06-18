# File Research: sources/virtualization/nvme-cli/libnvme/test/hkdf_add1.c

## Purpose
OpenSSL HKDF behavior probe/test.

## Behavior
Builds two HKDF contexts with the same SHA-256 salt/key. One derives with two `EVP_PKEY_CTX_add1_hkdf_info()` calls (`a` then `b`), the other with only `b`. If outputs match, the API behaved like set/replace and the test fails; if different, it prints `add` and succeeds.

## Relevance
Confirms OpenSSL HKDF info accumulation semantics needed by libnvme crypto/TLS key derivation expectations.
