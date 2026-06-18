# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_rquota.c

Purpose: hand-updated rpcgen-derived XDR routines for RQUOTA get/set quota arguments and results, including the extended protocol that carries quota type separately from id.

Important APIs and types: `xdr_sq_dqblk()`, `xdr_getquota_args()`, `xdr_setquota_args()`, `xdr_ext_getquota_args()`, `xdr_ext_setquota_args()`, `xdr_rquota()`, `xdr_qr_status()`, `xdr_getquota_rslt()`, `xdr_setquota_rslt()`, `sq_dqblk`, `rquota`, `getquota_rslt`, and `setquota_rslt`.

Control flow: quota block and quota result structures use optimized inline encode/decode paths for fixed 8-word and 10-word payloads, with scalar XDR fallback and generic XDR_FREE handling. Argument routines serialize bounded path strings, ids, qcmd, optional type, and quota blocks. Result routines serialize status first and include the quota union arm only for `Q_OK`; `Q_NOQUOTA` and `Q_EPERM` carry no payload and unknown statuses fail.

State and persistence: no local state. XDR decode may allocate path strings through `xdr_string()` and XDR_FREE releases them.

Dependencies and integration points: included only when RQUOTA build support is enabled. It feeds the RQUOTA protocol handlers such as `rquota_setquota.c` and must match structures in `rquota.h`.

Risks: all quota quantities are 32-bit wire values, so backend 64-bit quota values may be truncated elsewhere. Inline paths assume exact field counts and byte order helpers. Paths are bounded by `RQ_PATHLEN`, but handler-side export resolution still determines semantic validity.

Test signals: round-trip fixed quota blocks through inline and fallback XDR paths, legacy and extended get/set args, each result status, unknown status rejection, maximum path lengths, and XDR_FREE for decoded path strings.
