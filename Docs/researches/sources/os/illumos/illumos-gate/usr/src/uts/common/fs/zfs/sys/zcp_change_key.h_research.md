# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_change_key.h

This header declares channel-program synctask helpers for changing dataset encryption keys.

Public API surface:
- `zcp_synctask_change_key_cleanup()` releases task-specific state.
- `zcp_synctask_change_key_check()` validates the change-key operation in synctask check context.
- `zcp_synctask_change_key_sync()` applies the operation in sync context.
- `zcp_synctask_change_key_create_params()` builds `dsl_crypto_params_t` from key bytes and key format.

Risk-sensitive invariants:
- Key material and crypto params require explicit cleanup discipline.
- Check and sync phases must agree on validated state and operate under DMU transaction rules.
