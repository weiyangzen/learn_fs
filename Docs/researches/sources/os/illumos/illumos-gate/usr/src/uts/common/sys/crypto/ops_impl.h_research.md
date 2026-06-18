# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ops_impl.h

Internal request-parameter packaging layer for the kernel cryptographic framework scheduler. It defines compact per-operation parameter bundles, operation group/type enums, and macros that marshal KCF API/ioctl arguments into a single `kcf_req_params_t` passed to providers.

Key elements:
- Defines operation-parameter structs for digest, MAC, encrypt, decrypt, sign, verify, encrypt+MAC, MAC+decrypt, random, session, object, key, provider-management, and no-store key operations.
- `kcf_op_type_t` enumerates init/single/update/final/atomic operation phases plus digest-key, MAC-verify, dual cipher/MAC, recover, random, session, object, key, key-check, and provider-management operations.
- `kcf_op_group_t` groups request payload unions by provider function families, including operations without mechanisms such as sessions and objects.
- `IS_INIT_OP`, `IS_SINGLE_OP`, `IS_UPDATE_OP`, `IS_FINAL_OP`, and `IS_ATOMIC_OP` classify operation types used by KCF dispatch logic.
- `kcf_req_params_t` stores the group, operation type, and a union of the corresponding parameter bundle.
- `KCF_WRAP_*_OPS_PARAMS` macros fill request bundles in-place and preserve the framework mechanism type before provider mechanism-number translation.
- Session and provider-management wrappers carry an explicit provider descriptor for cases where a logical provider supplies the handle but another provider supplies the ops vector.
- Key wrappers handle stored-object and no-store variants, including public/private key-pair templates and output templates.
- `KCF_SET_PROVIDER_MECHNUM` translates a framework mechanism number into a provider-local mechanism number before SPI invocation.

Dependencies:
- Depends on KCF provider descriptors and mechanism translation from `sys/crypto/impl.h`, provider SPI types from `spi.h`, and public crypto data/key/mechanism types from `api.h` and `common.h`.
- Used by ioctl and kernel crypto API front ends before submission through scheduler routines declared in `sched_impl.h`.

Research notes:
- The wrapper macros intentionally copy `crypto_mechanism_t` by value but store data/key/template pointers; caller lifetimes still matter for synchronous versus asynchronous paths.
- Some struct fields are generic to keep the union small; comments identify reused fields for wrap/unwrap and key-pair public/private variants.
- Mechanism translation is split from initial wrapping so KCF can retain both framework and provider mechanism identities.
