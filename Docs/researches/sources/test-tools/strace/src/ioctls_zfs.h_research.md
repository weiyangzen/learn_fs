# sources/test-tools/strace/src/ioctls_zfs.h

Header containing ZFS ioctl command definitions or table fragments used by strace ioctl lookup/decoding. It has no runtime control flow but contributes constants/symbol names to ioctl command rendering. Dependencies are generated ioctl-table build code and ZFS ioctl numbering conventions. Risks are stale constants relative to OpenZFS, symbol collisions, and platform-specific availability. Tests should verify ioctl table generation includes these commands and traces render expected ZFS names rather than raw `_IOC` values.
