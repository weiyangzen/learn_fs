# File Research: sources/os/bsd/freebsd-src/sys/sys/ttyqueue.h

Kernel TTY input/output queue data structure and API header.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines `struct ttyinq` with block pointers, begin/line/reprint/end offsets, block count, and quota for canonical input buffering.
- Defines fixed input block payload size of 128 bytes.
- Defines `struct ttyoutq` with block pointers, begin/end offsets, block count, and quota for output buffering.
- Defines output block payload size based on a 256-byte block minus next pointer size.
- Declares input queue sizing, free, UIO read, write, no-fragment write, canonicalize, break-canonicalize, findchar, flush, peek, unput, reprint position, and iteration functions.
- Declares output queue flush, sizing, free, read, UIO read, write, and no-fragment write functions.
- Provides inline queue capacity/usage helpers with `MPASS` invariants.

Dependencies:
- Kernel-only APIs depend on `struct tty`, `struct uio`, and queue block implementations elsewhere.

Notable risks:
- Canonical line state uses multiple offsets into block chains; off-by-one or incorrect flush/canonicalize transitions can corrupt terminal input semantics.
- Quota and high-water logic must stay synchronized with `tty.h` watermark flags.
