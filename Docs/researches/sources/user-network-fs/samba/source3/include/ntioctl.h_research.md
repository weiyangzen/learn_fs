# sources/user-network-fs/samba/source3/include/ntioctl.h

## Purpose
`ntioctl.h` defines the data shape for NT filesystem ioctl support currently represented here by shadow copy enumeration data. It supports FSCTL-style paths that expose Windows previous-version labels.

## Important APIs, Types, And Control Flow
`SHADOW_COPY_LABEL` is a 25-byte character array sized for labels such as `@GMT-2004.02.18-15.44.00` plus a terminator. `struct shadow_copy_data` contains `num_volumes` and a pointer to a concatenated list of labels. No functions are declared.

## State And Persistence
The structure is transient response state. `num_volumes` reports mounted shadow volumes, and `labels` points to memory owned by the caller or provider. Persistent snapshot data is managed by VFS shadow copy modules and the underlying filesystem, not this header.

## Dependencies And Integration Points
It integrates with FSCTL_GET_SHADOW_COPY_DATA handling, VFS shadow copy providers, SMB ioctl response construction, and clients listing previous versions. It depends only on fixed-width integer types and Samba allocation conventions in consumers.

## Risks And Test Signals
Risks include fixed label length mismatches, missing NUL termination, incorrect concatenation sizing, and confusing mounted snapshot count with returned label count. Test signals include shadow copy enumeration with zero, one, and many labels; exact label length boundary checks; malformed provider data rejection; SMB ioctl response size validation; and Windows client previous-versions browsing.
