# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_names.h

## Purpose
Defines standard SCSI name-string prefixes and maximum string lengths.

## Main Interfaces
- Prefix strings: `SNS_EUI`, `SNS_IQN`, `SNS_MAC`, `SNS_NAA`, `SNS_WWN`.
- Maximum raw lengths for EUI, IQN, MAC, NAA, and WWN.
- Maximum full string lengths: `SNS_EUI_LEN_MAX`, `SNS_IQN_LEN_MAX`, `SNS_MAC_LEN_MAX`, `SNS_NAA_LEN_MAX`, `SNS_WWN_LEN_MAX`, `SNS_LEN_MAX`.

## Dependencies And Relationships
Standalone naming utility header for SCSI identifiers, likely used by iSCSI/SCSI unit-address and device identification code.

## Research Notes
`SNS_LEN_MAX` is set to the IQN maximum, making IQN the limiting name-string length.

## Notable Risks
- The macros using `sizeof (SNS_*)` include the terminating NUL, so callers must understand whether the length is buffer size or string payload length.
