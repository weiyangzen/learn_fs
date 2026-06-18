# File Research: sources/os/linux/linux/fs/dlm/member.h

## Role

`member.h` declares membership and slot-management APIs used by recovery, RCOM, and lockspace code.

## Exported Interface

It exposes lockspace stop/start, member clearing, recovery membership reconciliation, member/removed queries, slot version/copy/assign helpers, and `dlm_lsop_recover_done()`.

## Research Notes

Read completely. The declarations correspond directly to `member.c`.
