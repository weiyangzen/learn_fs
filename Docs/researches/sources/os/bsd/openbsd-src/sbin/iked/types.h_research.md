# File Research: sources/os/bsd/openbsd-src/sbin/iked/types.h

This shared OpenIKED header defines global constants, default paths, option flags, transform metadata, IPC message types, privilege-separated process IDs, and reset modes.

Key contents:
- Default runtime user/config/socket/CA paths:
  - `_iked`
  - `/etc/iked.conf`
  - `/var/run/iked.sock`
  - `/etc/iked/` and certificate/key subdirectories
- Vendor/NAS identity strings used in IKE/RADIUS paths.
- Runtime option flags for verbose, no-action, and passive modes.
- IKE/NAT-T ports, nonce/cookie size limits, max message/config/tag/password sizes, and default lifetimes.
- `struct iked_constmap` for ID-to-name mappings.
- `struct iked_transform` for IKEv2 transform metadata and scoring.
- `enum imsg_type`, covering control messages, compile/config load messages, UDP/PF_KEY/IKE message passing, RADIUS config, virtual route/DNS/address changes, OCSP, auth/key operations, stats, and process-fd readiness.
- `enum privsep_procid` for parent, control, cert, and IKEv2 processes.
- `enum flushmode` for reload/reset scopes.
- Local `nitems` fallback macro.

Security and correctness notes:
- This header is a contract between multiple OpenIKED processes; enum ordering and message IDs must stay consistent across all participants.
- Size constants constrain fixed buffers in identity, PSK, message, and CP code.
