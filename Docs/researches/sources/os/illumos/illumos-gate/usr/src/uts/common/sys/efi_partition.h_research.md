# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi_partition.h

This header defines the on-disk GPT/EFI partition structures, well-known partition type GUIDs, Solaris GPT abstraction structures, and userland libefi helper prototypes.

Key contents:
- GPT label constants, GPT signature, EFI header size workaround, and reserved padding size calculation.
- On-disk little-endian GPT header `efi_gpt_t`.
- GPT entry attribute bitfield `efi_gpe_Attrs_t`.
- Partition type GUID macros for Solaris/illumos partition roles, EFI system/legacy MBR, Symantec, Microsoft reserved, Dell, Apple HFS/UFS/ZFS/APFS, FreeBSD boot/swap/UFS/Vinum/ZFS, and BIOS boot.
- Minimum partition array and reserved partition sizes.
- GPT partition entry `efi_gpe_t`.
- Solaris library partition abstraction `dk_part_t`.
- Solaris GPT abstraction `dk_gpt_t`, including version, partition count, LBA sizing/bounds, disk GUID, flags, alternate LBA, and flexible partition array.
- GPT corruption flag `EFI_GPT_PRIMARY_CORRUPT`.
- Private libefi/driver ioctl payload `dk_efi_t`.
- 64-bit partition descriptor `partition64`.
- `EFI_NUMPAR`.
- Userland libefi prototypes under `!_KERNEL`: allocation, read, write, free, type, error check, auto sense, reserved sectors, and whole-disk helpers.

Dependencies:
- Includes `sys/uuid.h` and `sys/stddef.h`.
- Uses `diskaddr_t`, `uint_t`, `ushort_t`, and `len_t`.
- Uses C++ guards.

Research notes:
- The comment explains that some AMI EFI firmware expects the header size to be 92 bytes rather than `sizeof (efi_gpt_t)`, so `EFI_HEADER_SIZE` intentionally stops before reserved padding.
- The header bridges on-disk GPT structures and Solaris VTOC-like abstractions used by libefi and drivers.
- Filesystem/storage relevance is direct: this is the partition-table format used to discover and manage disk slices/partitions for filesystems and block devices.
