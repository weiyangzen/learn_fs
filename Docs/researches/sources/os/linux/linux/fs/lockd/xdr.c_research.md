# File Research: sources/os/linux/linux/fs/lockd/xdr.c

## Purpose
`xdr.c` implements legacy NLM server XDR encode/decode routines for lockd, covering NLM v1/v3-style arguments and replies.

## Main Responsibilities
- Converts 32-bit protocol offsets/lengths to and from `loff_t`, saturating encode to `NLM_OFFSET_MAX`.
- Decodes NLM file handles constrained to exactly `NFS2_FHSIZE`.
- Decodes legacy NLM locks into `struct nlm_lock` plus initialized `struct file_lock`.
- Encodes conflicting lock holders for TEST replies.
- Decodes call arguments for TEST, LOCK, CANCEL, UNLOCK, RES, SM_NOTIFY, SHARE, and FREE_ALL/NOTIFY.
- Encodes replies for TEST, generic status, void, and SHARE.

## Key Decode Behavior
- `svcxdr_decode_lock()` reads caller, NFSv2 file handle, owner handle, svid, signed 32-bit start, and signed 32-bit length. It initializes a POSIX read lock and computes `fl_start`/`fl_end`, treating zero or wrapping length as to-EOF.
- `nlmsvc_decode_testargs()` decodes cookie, exclusive flag, and lock; exclusive sets `F_WRLCK`.
- `nlmsvc_decode_lockargs()` additionally decodes block, reclaim, state, and defaults `monitor = 1`.
- `nlmsvc_decode_cancargs()` decodes block/exclusive/lock.
- `nlmsvc_decode_unlockargs()` forces `F_UNLCK`.
- `nlmsvc_decode_shareargs()` initializes a pseudo share lock with `LOCKD_SHARE_SVID`, then decodes cookie, caller, file handle, owner, mode, and access.
- `nlmsvc_decode_notify()` decodes caller name and state for FREE_ALL-like notify handling.

## Key Encode Behavior
- TEST replies encode cookie and status; when denied, they also encode holder exclusivity, svid, owner handle, start, and length.
- Generic replies encode cookie and status.
- SHARE replies encode cookie, status, and a zero sequence value.

## Integration Points
- Uses inline primitive helpers from `svcxdr.h`.
- Implements prototypes declared in `xdr.h`.
- Used by the NLM v1/v3 procedure table in `svcproc.c`.

## Risks and Edge Cases
- File handles are rejected unless exactly NFSv2-sized despite broader protocol descriptions.
- Share argument range checks are explicitly called out as missing in a comment.
- Decoded caller and owner data point into the XDR stream.
- Legacy 32-bit ranges can overflow or be clamped when encoded back from `loff_t`.
