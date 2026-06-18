# File Research: sources/os/linux/linux-stable/fs/lockd/nlm.h

Defines core Network Lock Manager protocol constants.

Contents:
- Maximum v1/v3 and v4 lock offsets.
- NLM status enum values:
  - granted, denied, nolocks, blocked, grace-period denied
  - v4-only deadlock, read-only filesystem, stale file handle, file too big, failed
- NLM RPC program number `100021`.
- Procedure numbers for NULL, TEST, LOCK, CANCEL, UNLOCK, GRANTED, async message/result variants, NSM notify, SHARE/UNSHARE, NM_LOCK, and FREE_ALL.
