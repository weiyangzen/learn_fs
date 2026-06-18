# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/uccid.h

## Purpose
User-facing ioctl ABI for the USB CCID smart-card driver.

## Main Interfaces
- Defines APDU and ATR maximum sizes.
- Defines ioctl base `UCCID_IOCTL`, version constants, and current version.
- Defines transaction commands `UCCID_CMD_TXN_BEGIN` and `UCCID_CMD_TXN_END` with flags for nonblocking, reset, and release behavior.
- Defines status command `UCCID_CMD_STATUS` and status flags for card presence, active card, product, serial, and parameters validity.
- Defines ICC modification command `UCCID_CMD_ICC_MODIFY` and actions for power on, power off, and warm reset.
- Defines payload structures `uccid_cmd_txn_begin_t`, `uccid_cmd_txn_end_t`, `uccid_cmd_status_t`, and `uccid_cmd_icc_modify_t`, plus status enum.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/usb/clients/ccid/ccid.h`. It is the user/kernel ABI layer above the lower-level CCID USB protocol definitions.

## Research Notes
The ioctl structs carry version fields, which allows future ABI extension while preserving current command numbers.
