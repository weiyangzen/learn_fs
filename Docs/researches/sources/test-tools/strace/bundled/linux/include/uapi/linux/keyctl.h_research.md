# sources/test-tools/strace/bundled/linux/include/uapi/linux/keyctl.h

Purpose: declares command IDs, special keyring IDs, default request-key destinations, cryptographic parameter structures, move/capability flags, and notification capability bits for the `keyctl(2)` syscall.

Important APIs/types/functions: constants cover `KEY_SPEC_*`, `KEY_REQKEY_DEFL_*`, `KEYCTL_*` commands through watch support, `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, `keyctl_pkey_params`, `KEYCTL_MOVE_EXCL`, and `KEYCTL_CAPS*` feature bits.

Control flow: userspace calls `keyctl` with a command selector and command-specific scalar or pointer arguments. Commands manage keyrings, update/revoke/link/search/read keys, instantiate request-key results, compute DH/KDF/public-key operations, restrict/move keys, query capabilities, or watch keys.

State/persistence behavior: many commands mutate persistent keyring/key objects scoped to thread, process, session, UID, group, namespace, or requestor contexts. Capabilities and describe/read queries are observational.

Dependencies/integration: depends on Linux integer types and integrates with kernel key retention service, request-key upcalls, LSM labels, watch queues, and crypto providers.

Risks and test signals: command-specific argument layouts are easy to misdecode. Tests should cover negative special IDs, C++ `private` field compatibility, public-key query structs, capability byte arrays, key movement, and watch-key command decoding.
