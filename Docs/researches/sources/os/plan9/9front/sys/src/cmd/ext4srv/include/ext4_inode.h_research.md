# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_inode.h

Inode accessor API header.

Key behavior:
- Declares getters/setters for mode, UID/GID, size, access/change/modify/delete/create times, link count, blocks count, flags, generation, extra inode size, file ACL, direct and indirect block slots, and device number.
- Declares inode type predicates and flag set/clear/test helpers.
- Declares inode checksum getter/setter.
- Declares truncate eligibility and extent-root access.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`; forward-declares `ext4_extent_header` as incomplete.
- Implemented by `ext4_inode.c` and used throughout filesystem, directory, public API, mkfs, and service code.

Research notes:
- The API abstracts endian conversion and OS-specific inode layout details from callers.
- It exposes no high-resolution timestamp extra fields beyond raw creation time.
