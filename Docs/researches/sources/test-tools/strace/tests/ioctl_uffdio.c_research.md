<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_uffdio.c -->
# sources/test-tools/strace/tests/ioctl_uffdio.c

Purpose: Exercises userfaultfd ioctl decoding for API negotiation, memory registration, copy, zeropage, wake, unregister, write-protect, continue, and poison requests.

Important APIs/types/functions: Uses `userfaultfd` via `syscall(__NR_userfaultfd, O_NONBLOCK)`, `ioctl`, `mmap`, `madvise`, `getpagesize`, `struct uffdio_api`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_range`, `uffdio_writeprotect`, `uffdio_continue`, and `uffdio_poison`. It also uses `xlat/uffd_api_features.h` to print negotiated features.

Control flow: First it runs every supported UFFDIO request against fd `-1` with NULL and zeroed structure pointers. It then creates a real nonblocking userfaultfd, negotiates `UFFDIO_API`, maps two anonymous pages, registers one page for missing faults, copies data into the registered page, tests invalid copy mode bits, zeropages, wakes, unregisters, write-protects, continues, and poisons.

State/persistence behavior: The only kernel state is a transient userfaultfd registration and anonymous memory mappings inside the process. The code avoids touching the registered missing-fault area except through userfaultfd ioctls to prevent a self-stall.

Dependencies: Requires `__NR_userfaultfd`, Linux userfaultfd UAPI headers, anonymous mmap support, and kernel support for the newer ioctls guarded by header constants. Uses strace helpers and xlat feature tables.

Integration points: Validates strace decoding of nested `uffdio_range`, feature/ioctl bitmasks, output fields such as `copy`, `zeropage`, `mapped`, and `updated`, and unknown mode-bit fallbacks.

Risks: Kernel feature availability varies; some calls can fail legitimately while still testing decoder formatting. Userfaultfd semantics are sensitive to accidental memory access in the registered range.

Test signals: Expected output includes EBADF cases, API feature/ioctl bitsets on success, pointer/range formatting, DONTWAKE/WRITEPROTECT/POISON modes, and final clean exit.

Source read signal: complete file read for this research pass; file size 261 line(s), 8975 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_uffdio.c -->
