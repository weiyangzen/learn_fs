# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_reset_notify.h

This header defines SCSI HBA reset notification registration state and helper prototypes.

Key definitions:
- `struct scsi_reset_notify_entry` stores:
  - target `scsi_address`
  - callback function
  - callback argument
  - next-list pointer
- Lock lint annotation states entries are protected by the lock passed as an argument.
- Declares kernel helpers:
  - `scsi_hba_reset_notify_setup()`
  - `scsi_hba_reset_notify_tear_down()`
  - `scsi_hba_reset_notify_callback()`

Dependencies:
- Includes `sys/note.h` and `sys/scsi/scsi_types.h`.

Impact:
- Used by adapter drivers to maintain target-driver reset notification callback lists.

Cautions:
- Correct use depends on callers passing and holding the intended mutex during list manipulation/callback flow.
