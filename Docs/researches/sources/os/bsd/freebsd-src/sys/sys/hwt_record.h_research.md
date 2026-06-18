# File Research: sources/os/bsd/freebsd-src/sys/sys/hwt_record.h

Defines the shared hardware-tracing record type enum used by both user ABI and kernel internals. Record kinds cover `MMAP`, `MUNMAP`, `EXECUTABLE`, `KERNEL`, thread create/name events, and trace buffer records.

Under `_KERNEL`, `struct hwt_record_entry` adds a `TAILQ_ENTRY` link and stores the kernel-side representation of each record. Path-bearing records use dynamically referenced `char *fullpath` plus address/base address; buffer records carry buffer id, current page, and offset; thread events carry a thread id.

This file is deliberately narrow and pairs with `hwt.h`, which defines the user-copy ABI form.
