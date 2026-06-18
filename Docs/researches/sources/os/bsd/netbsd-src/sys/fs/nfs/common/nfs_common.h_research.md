# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_common.h

## Purpose
Provides shared NFS XDR build/dissection helpers and type-conversion macros for common NFS encode/decode paths.

## Main Interfaces
- Extern arrays `nv3tov_type` and `nfsv3_type` convert between NFSv3 wire file types and vnode types.
- `vtonfsv2_mode`, `nfsv3tov_type`, and `vtonfsv3_type` convert vnode type/mode to NFS wire values.
- Declares lower helpers `nfs_adv`, `nfsm_disct`, `nfs_realign`, `nfsm_build_xx`, `nfsm_dissect_xx`, `nfsm_dissect_xx_nonblock`, `nfsm_strsiz_xx`, and `nfsm_adv_xx`.
- Macros `nfsm_build`, `nfsm_dissect`, `nfsm_dissect_nonblock`, `nfsm_strsiz`, `nfsm_mtouio`, and `nfsm_adv` wrap helper calls and enforce common error handling via `goto nfsmout`.
- Defines `nfsm_rndup` for XDR four-byte alignment and `nfsm_aligned` depending on strict-alignment architecture.

## Integration
Used by NFS encode/decode code that follows the classic local-variable convention (`mb`, `bpos`, `md`, `dpos`, `mrep`, `error`, `nfsmout`).

## Risks
- Macro control flow requires callers to define expected local variable names and a `nfsmout` label.
- Incorrect size/alignment inputs can cause bad XDR parsing or mbuf traversal errors.
