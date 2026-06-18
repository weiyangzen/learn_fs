# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crypto.c

Implements libnvme cryptographic support for DH-HMAC-CHAP, NVMe/TCP TLS PSKs, Linux keyrings, host ID generation, and host NQN/ID configuration file reads.

Major feature gates:
- Without `CONFIG_OPENSSL`, HMAC/TLS derivation functions either pass through `LIBNVME_HMAC_ALG_NONE` secrets or return `-ENOTSUP` with log messages.
- With `CONFIG_OPENSSL`, HMAC and HKDF are implemented using OpenSSL EVP APIs.
- Without `CONFIG_KEYUTILS`, keyring functions return `-ENOTSUP`, while config import returns zero IDs.

OpenSSL-backed crypto:
- `default_hmac()` maps key length 32/48/64 to SHA-256/SHA-384/SHA-512 defaults, though TLS key derivation mostly accepts SHA-256 and SHA-384.
- `select_hmac()` maps libnvme HMAC IDs to OpenSSL digests and digest lengths.
- `libnvme_gen_dhchap_key()` derives DH-HMAC-CHAP keys using HMAC over host NQN and `"NVMe-over-Fabrics"`.
- `derive_retained_key()` and `_compat()` derive retained PSKs from configured PSKs with HKDF.
- `derive_tls_key()` and `_compat()` derive TLS PSKs from retained PSKs and identities.
- `derive_psk_digest()` builds a Base64 HMAC digest for NVMe TLS identity version 1.

TLS key lifecycle:
- `libnvme_create_raw_secret()` accepts generated random secret, `pin:` deterministic secret, or hex secret, enforcing key lengths of 32/48/64 bytes.
- `libnvme_generate_tls_key_identity()` and `_compat()` derive keys and return an identity string.
- `libnvme_export_tls_key_versioned()` creates `NVMeTLSkey-<v>:<hmac>:<base64(raw+crc)>:` strings.
- `libnvme_import_tls_key_versioned()` validates version, HMAC, encoded length, Base64, decoded length, and CRC before returning key bytes.
- Compatibility wrappers preserve older import/export APIs.

Linux keyutils integration:
- Looks up or links keyrings, reads keys, searches keys, updates/revokes existing keys, scans TLS keys, and imports keys from controller config.
- Default keyring is `.nvme`.
- `__libnvme_import_keys_from_config()` ties controller TLS config into keyring IDs and key IDs used by fabrics connect option construction.

Host identity:
- Reads host NQN/ID from `LIBNVME_HOSTNQN` and `LIBNVME_HOSTID` environment variables or `/etc/nvme/hostnqn` and `/etc/nvme/hostid`.
- Generates host ID from DMI product UUID, DMI raw entries, IBM device-tree UUID, or random UUID fallback.
- Generates host NQN as `nqn.2014-08.org.nvmexpress:uuid:<hostid>`.

Dependencies:
- OpenSSL EVP/HMAC/KDF/core names when enabled.
- Linux keyutils when enabled.
- `base64.c`, `crc32.c`, cleanup helpers, private libnvme logging/path helpers, and UUID helpers.

Risks and notes:
- `getswordfish()` declares `counter` inside the loop, so multi-block deterministic output repeats the same SHA-256 block; for 48/64-byte outputs this weakens the derived secret pattern.
- Several identity strings are assembled with `sprintf` into buffers sized by estimates; current callers allocate expected sizes, but this is fragile against formula changes.
- `libnvme_import_tls_key_versioned()` only accepts version 1.
- `base64_encode()` does not NUL-terminate; callers rely on zeroed buffers or append terminators.
- Key material is generally freed but not explicitly zeroized before free.
- Tests should cover OpenSSL/no-OpenSSL, keyutils/no-keyutils, TLS key import/export round trips, CRC mismatch, hex secret parsing, `pin:` derivation, env/config host identity, and DMI fallback behavior.
