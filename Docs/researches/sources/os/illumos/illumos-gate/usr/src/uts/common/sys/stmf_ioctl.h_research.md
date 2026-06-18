# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_ioctl.h

## Role

User/kernel ioctl ABI for administering STMF logical units, target ports, sessions, groups, views, provider data, trace buffers, ALUA state, and default properties.

## Key Contents

Defines ioctl command numbers under the STMF namespace and version `STMF_VERSION_1`. Defines `stmf_iocdata_t`, which carries input/output buffer sizes, entry counts, errors, and 64-bit buffer addresses.

Defines list entries for LUs, target ports, and SCSI sessions; LU/LPORT/STMF states; config states; LU and target-port property structures; state descriptors; ALUA state descriptor; ioctl-specific error codes; group names and group-entry identifiers; group operation data; view-entry operation data; provider private data ioctl payload; and default property setting structure.

Also defines SCSI device identifier descriptors and protocol/code-set/association/identifier type constants.

## Interfaces

Declares `stmf_copyin_iocdata` and `stmf_copyout_iocdata`.

## Design Notes

The ABI uses fixed-size identifiers and flexible trailing data conventions. Many structures carry validity bits so ioctl payloads can represent partial updates.
