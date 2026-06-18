# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_oplock.c

## Purpose

`smb_oplock.c` contains SMB1-specific oplock support. It adapts SMB1 oplock requests, acknowledgements, and break notifications to the common SMB oplock engine while preserving SMB1 wire encodings and dialect-specific behavior.

## Main Interfaces

- `smb1_oplock_ack_break()` handles SMB1 `Locking_andX` oplock break acknowledgements.
- `smb1_oplock_send_break()` sends an SMB1 oplock break notification or performs a local break if the client cannot be reached or does not acknowledge.
- `smb1_oplock_acquire()` translates requested SMB1 oplock levels into internal oplock levels, calls common oplock request logic, and translates the result back to SMB1.

## Behavior And Data Flow

Break acknowledgement maps SMB1 `oplock_level == 0` to `OPLOCK_LEVEL_NONE` and any nonzero level to `OPLOCK_LEVEL_TWO`. It enters the node ofile list, takes `node->n_oplock.ol_mutex`, clears `og_breaking`, wakes waiters on `og_ack_cv`, calls common `smb_oplock_ack_break()`, and updates `ofile->f_oplock.og_state`.

Break notification composes a full SMB1 `SMB_COM_LOCKING_ANDX` response in the request reply chain, including a synthetic header and `LOCKING_ANDX_OPLOCK_RELEASE`. Internal break levels are converted to SMB1 values: none is `0`, level II is `1`.

`smb1_oplock_send_break()` downgrades level-II breaks to none for pre-NT dialect clients lacking level-II support. If `smb_session_send()` fails, it closes the ofile. If an acknowledgement is required and `smb_oplock_wait_ack()` fails, it performs the acknowledgement locally, always breaking to none.

Acquire logic rejects non-disk trees and trees without oplocks, honors session level-II capability, maps `SMB_OPLOCK_BATCH`, `SMB_OPLOCK_EXCLUSIVE`, and `SMB_OPLOCK_LEVEL_II` to internal states, optionally forces level-II for `SMB_TREE_FORCE_L2_OPLOCK`, tries exclusive/batch first, then level-II fallback if allowed.

## Dependencies

This file relies on common oplock helpers (`smb_oplock_request`, `smb_oplock_ack_break`, `smb_oplock_wait_ack`, `smb_oplock_wait_break`), SMB1 message encoding, session send, ofile close, tree feature flags, and per-node oplock locks.

## Notable Invariants And Risks

- All state mutation of `ofile->f_oplock` during ack/local-ack occurs under `node->n_oplock.ol_mutex`.
- SMB1 never has durable handles or granular oplocks; this file intentionally avoids SMB2 lease/durable semantics.
- `og_dialect` records whether the client can receive level-II breaks, independent of the negotiated SMB dialect.
- Failure to send a break closes the ofile rather than leaving stale caching rights.
- Timeout/no-ack handling logs in debug builds and falls back to local break-to-none.
