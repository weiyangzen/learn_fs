# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/spi.h

Cryptographic Service Provider Interface header. It defines provider registration structures, provider operation vectors, request/context handles, mechanism capability masks, provider status, and callbacks exported by the kernel cryptographic framework to providers.

Key elements:
- Defines SPI interface versions 1 through 4 and provider-private, context-template, and request-handle opaque types.
- `crypto_ctx_t` is the provider-facing operation context with provider/session handles, provider-private and framework-private slots, flags, and operation state.
- Extended token/provider flag constants mirror PKCS#11 token-info state such as RNG, write protection, login requirement, token initialized, and PIN warning/lock states.
- Operation-vector structs cover control, context/template management, digest, cipher, MAC, sign, verify, old dual operations, dual cipher/MAC operations, random, session, object, key, provider management, mechanism copyin/copyout/free, no-store key, and FIPS 140 POST hooks.
- Versioned `crypto_ops_v1` through `crypto_ops_v4` extend the provider ops vector by adding mechanism ops, no-store key ops, and FIPS 140 ops.
- `crypto_provider_dev_t` identifies software providers by module linkage and hardware/logical providers by `dev_info_t`.
- `crypto_func_group_t` masks describe which function groups each provider mechanism supports, including atomic and dual-operation capabilities.
- Defines simple and dual function-group masks for internal KCF checks.
- `crypto_mech_info_t` describes a provider mechanism name, provider mechanism number, supported function groups, key-size range, and mechanism flags.
- `crypto_provider_info_t` describes provider registration state: interface version, description, type, device, provider handle, ops vector, mechanism list, logical-provider membership, and provider flags.
- Provider flags hide providers behind logical providers, indicate hash/HMAC update limitations, and mark synchronous providers.
- Exports provider lifecycle/completion functions: `crypto_register_provider`, `crypto_unregister_provider`, `crypto_provider_notification`, `crypto_op_notification`, and `crypto_kmflag`.

Dependencies:
- Kernel-only portions depend on DDI device types, memory allocation flags, module linkage, and public crypto common structures.
- Included by provider drivers/modules and by KCF internals that dispatch through provider operation vectors.

Research notes:
- The versioned ops union is append-style ABI evolution; accessor macros flatten the current view but providers must set the matching interface version.
- Provider mechanism numbers are provider-local; KCF maps framework mechanism IDs before invoking SPI callbacks.
- Request handles are how asynchronous providers report completion back to KCF; software fast-path requests use special handles to communicate allocation constraints.
