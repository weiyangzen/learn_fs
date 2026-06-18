# sources/test-tools/strace/src/ubi.c

Purpose: ioctl decoder for Linux UBI and UBI volume operations.

Important APIs/types/functions: `ubi_ioctl`, decoders for `UBI_IOCMKVOL`, `IOCRSVOL`, `IOCRNVOL`, `IOCEBCH`, `IOCATT`, `IOCEBMAP`, and `IOCSETVOLPROP`, plus xlat tables for volume types, flags, properties, and data types.

Control flow: structured ioctls fetch request structs and print relevant fields. Create volume and attach decode input on entry and, on successful exit, print changed integer fields using `tprint_value_changed`. Rename volume prints an array of rename entries bounded by requested count. Simpler ioctls print int/int64 pointed values or no arguments.

State and persistence behavior: stateless; reads tracee ioctl argument structures.

Dependencies and integration points: called by generic ioctl dispatch for UBI command numbers; depends on `<mtd/ubi-user.h>`, Linux ioctl definitions, and tracee memory printers.

Risks: name lengths from tracee structures must be clamped to fixed array sizes. Entry/exit split matters for commands that kernel mutates. Unknown commands fall back as decoded without argument details.

Test signals: make/resize/rename/change/attach/map/set-property, volume update int64, detach/remove/erase/map checks with int pointers, no-arg block create/remove, bad pointers, excessive name lengths, and successful exit value changes.
