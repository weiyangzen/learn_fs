# File Research: sources/os/bsd/freebsd-src/sys/sys/ucoredump.h

Kernel coredump writer and coredumper registration interface.

Key responsibilities:
- Defines coredump writer callback types for initialization, write, and extend operations.
- Defines vnode-backed writer context, public vnode writer/extend function declarations, `struct coredump_writer`, and `struct coredump_params`.
- Defines core output buffer size and declares `core_write`, `core_output`, and sbuf drain helper.
- Exposes tunables for packing file/vmmap info and compressing user cores.
- Defines coredumper probe priorities and coredumper probe/handle callbacks.
- Defines `struct coredumper` with list linkage, name, callbacks, and blockcount reference counter.
- Declares coredumper register/unregister.

Dependencies:
- Kernel-only; includes `_uio`, blockcount, and queue headers; depends on vnode, compressor, ucred, thread, and sbuf types.

Notable risks:
- Coredumper handle callbacks are documented to enter with the proc lock held and return with it dropped, a non-obvious ownership transfer.
- Probe callbacks run under the proc lock and must not sleep.
