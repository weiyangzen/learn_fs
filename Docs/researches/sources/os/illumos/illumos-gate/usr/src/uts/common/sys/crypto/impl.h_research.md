# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/impl.h

## Role

Defines private Kernel Cryptographic Framework implementation structures, provider tables, policy state, mechanism tables, provider operation wrappers, and internal exported functions.

## Kstats and Per-CPU Provider State

- `kcf_prov_stats_t`: provider total/passed/failed/busy statistics.
- `kcf_stats_t`: framework thread pool, queue, and taskq stats.
- `CPU_SEQID`: current CPU sequential id.
- `kcf_lock_withpad_t`: padded mutex.
- `kcf_prov_cpu_t`: per-CPU provider counters and hold/job counts, padded for cacheline isolation.
- `KCF_PROV_LOAD(pd)`: approximate provider load using refcount or taskq allocation count if busy.

## Provider State

- Provider states:
  - allocated
  - unverified
  - unverified FIPS140
  - verification failed
  - ready
  - busy
  - failed
  - disabled
  - unregistering
  - unregistered
- Macros:
  - `KCF_IS_PROV_UNVERIFIED()`
  - `KCF_IS_PROV_USABLE()`
  - `KCF_IS_PROV_REMOVED()`
- Internal flag:
  - `KCF_LPROV_MEMBER`

## Provider Descriptor

- `kcf_provider_desc_t` contains:
  - provider type and session id.
  - taskq.
  - per-CPU bins.
  - state lock/cv and state.
  - logical provider membership list.
  - provider handle and ops vector.
  - mechanism index table and mechanism list.
  - name, instance, module id, modctl.
  - description and flags.
  - hash/HMAC limits.
  - KCF-private handle and provider id.
  - kstat pointer and stats data.

Reference/job/stat macros manage per-CPU refcounts, job counts, completion signaling, and dispatch/failure/busy accounting.

## Mechanism Tables

- `crypto_mech_info_list_t`: valid second mechanisms for dual operations.
- `kcf_prov_mech_desc_t`: provider mechanism descriptor chain entry.
- `kcf_mech_entry_t`: mechanism table entry with name, id, hardware provider chain, software provider, hardware provider count, software generation, hardware threshold, parameter copyin function, and padding.
- Mechanism table limits:
  - digests, ciphers, MACs, sign/verify, key operations, misc.
- Global tables:
  - `kcf_digest_mechs_tab`
  - `kcf_cipher_mechs_tab`
  - `kcf_mac_mechs_tab`
  - `kcf_sign_mechs_tab`
  - `kcf_keyops_mechs_tab`
  - `kcf_misc_mechs_tab`
- Operation classes:
  - digest, cipher, MAC, sign, keyops, misc.
- ID helpers:
  - `KCF_MECHID()`
  - `KCF_MECH2CLASS()`
  - `KCF_MECH2INDEX()`
  - provider mechanism lookup macros.

## Policy and Software Configuration

- `kcf_policy_desc_t`: disabled-mechanism policy per provider/module, with refcount and mutex-protected disabled mechanism list.
- Policy refhold/refrele macros free descriptors on last release.
- `kcf_soft_conf_entry_t`: software module name plus mechanisms used as module autoload hints.
- Globals:
  - `soft_config_mutex`
  - `soft_config_list`

## Sessions and Minor State

- `crypto_provider_session_t`: links provider sessions to KCF provider descriptors.
- `crypto_session_data_t`: session lock/cv/flags, pre-approved amount, active contexts for digest/encrypt/decrypt/MAC/sign/verify/recover operations, provider, find cookie, provider session.
- Session flags:
  - in use
  - busy
  - closed
- `KCF_MAX_PIN_LEN`: 1024.
- `crypto_minor_t`: `/dev/crypto` minor state with refcount, lock/cv, session table, provider array, and provider sessions.
- `rc_project_crypto_mem`: project crypto memory resource-control handle.

## Internal Return Codes and RNG

- Internal status codes for mechanism lookup/table failure.
- `SUN_RANDOM`
- `CRYPTO_FG_RANDOM`: internal function group for random generation providers.

## Provider Ops Wrappers

The file defines extensive macros that call provider ops when present or return `CRYPTO_NOT_SUPPORTED` otherwise. Families include:

- Control/status.
- Context template creation/free.
- Mechanism copyin/copyout/free.
- Digest.
- Cipher encrypt/decrypt.
- MAC.
- Sign and sign recover.
- Verify and verify recover.
- Legacy dual operations.
- Dual cipher/MAC operations.
- Random seed/generate.
- Session open/close/login/logout.
- Object create/copy/destroy/get size/get/set attributes/find.
- Key generate/generate pair/wrap/unwrap/derive/check.
- Provider management: ext info, token init, PIN init/set.
- No-store key operations.

## Private KCF Entry Points

Exports internal routines from KCF to crypto/cryptoadmin modules, including:

- Single-operation digest/MAC/encrypt/decrypt/sign/verify variants.
- Digest-key provider operation.
- Dual update operations.
- Random seeding/generation.
- Provider info, mechanisms, token/PIN management.
- Administrative device/software provider list and disabled-mechanism configuration.
- Door loading, soft module unloading/loading.
- Mechanism number/function list/provider permitted mechanism building.
- Mechanism table init/add/remove/lookup.
- Provider descriptor allocation/free and registration undo/redo.
- RNG initialization and byte retrieval.
- Entropy insertion and poll support.
- Data movement helpers for `uio`, `mblk`, raw output/input, compare, digest data, block update across iov/uio/mblk.
- Key copy and attribute lookup.
- Parameter copyin helpers for AES CCM/GCM/GMAC and ECDH1.

## Provider and Policy Table Access

Provider table routines include init, add/remove, lookup by name/device/id, hardware provider table retrieval, slot list retrieval, provider table freeing, software provider lookup, and refcount query.

Policy routines include disabled-mechanism checks, policy table init, descriptor free, policy removal by name/device, lookup by name/device, loading disabled software/device policy, and removing soft config.

## Research Relevance

This is the central private KCF implementation header. It is essential for understanding provider registration, dispatch, mechanism lookup, policy enforcement, `/dev/crypto` session state, random provider plumbing, provider lifecycle, and how consumers are mapped to software/hardware crypto providers.
