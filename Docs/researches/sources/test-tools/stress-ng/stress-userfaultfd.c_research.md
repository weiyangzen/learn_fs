## sources/test-tools/stress-ng/stress-userfaultfd.c

Purpose: Implements `userfaultfd`, handling user-space page faults from a shared-VM cloned child.

Important APIs/types/functions: `stress_userfaultfd_info`, `stress_userfaultfd_supported`, `stress_userfaultfd_child`, `stress_userfaultfd_clone`, and `handle_page_fault`; uses `userfaultfd`, `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_COPY`, `UFFDIO_ZEROPAGE`, `UFFDIO_WAKE`, `poll`, `clone(CLONE_VM...)`, and OOM wrapper helpers.

Control flow: allocates a page-aligned zero page and anonymous region sized by `userfaultfd-bytes`, registers missing-page handling, clones a child sharing VM that repeatedly `madvise(MADV_DONTNEED)`s and writes each page, and parent polls/reads `uffd_msg` events. Each write fault is range-checked and resolved either by copying a zero page or zeropage ioctl.

State and persistence: anonymous mapping, userfault fd, clone stack, and OOM child lifecycle are transient. Metrics are updated continuously with nanoseconds per page fault.

Dependencies/integration: Linux userfaultfd headers/syscall, poll, clone, posix_memalign, nonblocking fd helper, OOMable stress-ng wrapper.

Risks: userfaultfd may be disabled or privilege-gated; failure to unregister, wake, or kill child could hang faulting memory; verify depends on write-fault flags.

Test signals: `VERIFY_ALWAYS`; validates API version, supported ioctls, event type, write flag, and address range.
