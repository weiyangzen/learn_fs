# File Research: sources/os/linux/linux/fs/lockd/nlm.h

Purpose: Declares core Network Lock Manager protocol constants.

Key contents:
- Defines NLMv1/v3 and NLMv4 maximum offset values.
- Enumerates lock status codes, with NLMv4-only extended errors under `CONFIG_LOCKD_V4`.
- Defines NLM RPC program number 100021.
- Defines procedure numbers for lock, unlock, cancel, async msg/res procedures, NSM notify, share/unshare, non-monitored lock, and free-all.

Dependencies and integration:
- Included by `lockd.h` and XDR/procedure table implementations.
- Status constants are used both as CPU values and converted to big-endian wire constants in `lockd.h`.

Risk notes:
- Procedure/status numeric values are protocol ABI and must not change.
