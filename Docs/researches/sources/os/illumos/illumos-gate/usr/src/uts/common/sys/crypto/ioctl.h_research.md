# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctl.h

User/kernel ioctl ABI for `/dev/crypto`. It defines command numbers, request payload structures, and 32-bit compatibility structures for PKCS#11-like cryptographic operations exposed through the illumos kernel cryptographic framework.

Key elements:
- Defines the `CRYPTO(x)` ioctl namespace, `CRYPTO_MAX_ATTRIBUTE_COUNT`, `CRYPTO_IOFLAGS_RW_SESSION`, `CRYPTO_INPLACE_OPERATION`, selected PKCS#11 mechanism constants, and threshold metadata used by provider capability reporting.
- `crypto_function_list_t` describes provider-supported function groups plus hash/HMAC limits and per-mechanism thresholds.
- General ioctls expose provider function lists and mechanism-name to internal-number translation.
- Session and login ioctls cover open, close, close-all, login, and logout, with user PIN buffers passed by address/length.
- Cryptographic operation structs cover encrypt, decrypt, digest, MAC, sign, verify, recover variants, multipart init/update/final flows, and combined update operations such as digest-encrypt and decrypt-verify.
- Random-number ioctls expose seed and generate operations.
- Object-management ioctls cover create, copy, destroy, get/set attributes, get size, and find init/update/final.
- Key ioctls cover stored-object key generation, key-pair generation, wrap, unwrap, derive, plus no-store key-generation/derivation variants that return key material through attributes instead of provider object handles.
- Provider and mechanism ioctls expose provider lists, token/provider metadata, provider mechanisms, mechanism info, token/PIN initialization, global mechanism list, all-mechanism info, and provider-by-mechanism selection.
- `_KERNEL && _SYSCALL32` sections mirror pointer- and size-bearing structs with `caddr32_t`, `size32_t`, and packed layout where long-long alignment differs.

Dependencies:
- Uses core crypto ABI types from `sys/crypto/api.h`, `sys/crypto/spi.h`, and `sys/crypto/common.h`, including sessions, providers, mechanisms, keys, objects, attributes, and mechanism-info structures.
- Consumed by the `/dev/crypto` ioctl implementation and by userland libraries/tools that marshal these structures.

Research notes:
- This is an ABI header; field order, sizes, command numbers, and 32-bit translations are compatibility-sensitive.
- Several structs use trailing one-element arrays for variable-length lists, so callers must allocate enough space for count-dependent payloads.
- Many payloads carry raw user pointers and lengths; kernel handlers must copy in/out defensively and translate embedded crypto mechanism/key structures for 32-bit callers.
