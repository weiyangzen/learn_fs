# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_impl.h

`cpc_impl.h` defines private CPU performance counter control interfaces used by libcpc/kernel CPC. It includes bind flags, request flags and validation macros, CPC capability bits, syscall subcodes, ioctl numbers, event/attribute length limits, attribute/PIC/context structures, and 32-bit syscall argument form.

Kernel content defines context hash sizing, context/PIC flags, DTrace CPC interrupt/mask state enums, tick source macro by architecture, global CPC state, and functions for invalidation, passivation, CPU stop/programming, PCBE loading, DCPC registration, context allocation/free, request assignment/configuration, and config cleanup. Error subcodes enumerate invalid events, attributes, unavailable resources, conflicts, privilege failures, processor binding failure, and hypervisor access denial.
