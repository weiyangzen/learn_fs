# File Research: sources/os/linux/linux-stable/fs/dlm/member.h

## Purpose
`member.h` declares DLM membership and slot-management APIs.

## Exports
- Lockspace transitions: `dlm_ls_stop()`, `dlm_ls_start()`.
- Membership cleanup: `dlm_clear_members()`, `dlm_clear_members_gone()`.
- Recovery reconciliation: `dlm_recover_members()`.
- Queries: `dlm_is_removed()`, `dlm_is_member()`.
- Slot protocol: `dlm_slots_version()`, `dlm_slot_save()`, `dlm_slots_copy_out()`, `dlm_slots_copy_in()`, `dlm_slots_assign()`.
- Lockspace-op callback bridge: `dlm_lsop_recover_done()`.

## Notes
The declarations map directly to `member.c`.
