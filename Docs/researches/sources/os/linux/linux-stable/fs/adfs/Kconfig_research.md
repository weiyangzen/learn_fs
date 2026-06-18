# File Research: sources/os/linux/linux-stable/fs/adfs/Kconfig
- Purpose: Defines configuration options for Acorn Disc Filing System support.
- Main options: `ADFS_FS` enables read support; `ADFS_FS_RW` enables experimental write support.
- Integration: Appears under miscellaneous filesystems and controls `fs/adfs/Makefile`.
- Behavior: Write support is separately gated because the driver primarily targets reading ADFS media and has narrower write guarantees.
- Research notes: The split config matches code paths where update/writeback functions exist but are optional.
