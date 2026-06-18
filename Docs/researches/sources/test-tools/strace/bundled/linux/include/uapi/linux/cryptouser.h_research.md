# sources/test-tools/strace/bundled/linux/include/uapi/linux/cryptouser.h

Purpose: declares the crypto userspace configuration and reporting netlink ABI for algorithm management and introspection.

Important APIs/types/functions: message IDs are `CRYPTO_MSG_NEWALG`, `DELALG`, `UPDATEALG`, `GETALG`, `DELRNG`, and the deprecated `GETSTAT`. Attribute enum `crypto_attr_type_t` maps report/stat payload types. `struct crypto_user_alg` carries algorithm, driver, module, type, mask, refcount, and flags. Report structs describe larval, hash, cipher, block cipher, AEAD, compression, RNG, akcipher, KPP, acomp, and signature algorithms. Deprecated stat structs remain for ABI numbering.

Control flow: no local code executes. The implied flow is netlink request/response against the kernel crypto subsystem: create/update/delete algorithms, query algorithm metadata, or delete RNG state. Stat messages are explicitly marked unsupported.

State and persistence behavior: algorithm registry state is kernel-global and module-backed; this header only fixes message layouts. Report data is a snapshot of registered crypto algorithms. Deprecated stats remain layout-compatible but should not be used.

Dependencies: includes `<linux/types.h>` for fixed-width fields and depends on generic netlink framing outside this file.

Integration points: strace can decode crypto netlink message types, attributes, `crypto_user_alg`, and report payloads. Crypto tools depend on `CRYPTO_MAX_NAME` fixed-size strings.

Risks: `CRYPTOCFGA_MAX` is defined inside the enum block after `__CRYPTOCFGA_MAX`, an unusual but valid style to preserve UAPI. Deprecated stat attributes still occupy IDs; removing them from decoders would shift labels. `CRYPTO_REPORT_MAXSIZE` is based on the largest legacy report and can become stale if new report structs grow.

Test signals: netlink decode tests should include GETALG replies for hash/cipher/AEAD/RNG, deprecated stat attributes rendered as unsupported, and unknown future attributes beyond `CRYPTOCFGA_MAX`.
