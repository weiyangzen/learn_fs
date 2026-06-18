# File Research: sources/os/bsd/freebsd-src/sys/sys/mac.h

Defines the user/kernel ABI for Mandatory Access Control labels.

Key content:
- Establishes POSIX MAC visibility and label size constants:
  - `MAC_MAX_POLICY_NAME`
  - `MAC_MAX_LABEL_ELEMENT_NAME`
  - `MAC_MAX_LABEL_ELEMENT_DATA`
  - `MAC_MAX_LABEL_BUF_LEN`
- `struct mac` carries label text buffers across syscalls/ioctls with `m_buflen` and `m_string`.
- `mac_t` is a pointer to `struct mac`.
- Userland-only APIs include label allocation/free, text conversion, get/set label on fd/file/link/process/peer/pid, policy presence checks, type-specific prepare helpers, `mac_execve`, and `mac_syscall`.
- Defines userland config path `/etc/mac.conf`.

Research relevance:
- VFS, mount, mbuf packet tags, SysV IPC, shared memory, and filesystems can carry MAC labels.
- This file is the public ABI for MAC-aware tools and the structure used at syscall boundaries.

Cautions:
- Kernel policy hooks and internal label structures are not defined here.
- Userland declarations are hidden under `!_KERNEL`.
