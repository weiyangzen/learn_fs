# File Research: sources/os/linux/linux-stable/fs/pstore/Kconfig

## Summary
Defines Kconfig options for the generic pstore subsystem, pstore frontends, ramoops, pstore zone support, and pstore block backend sizing/configuration.

## Main Responsibilities
- Expose `PSTORE` as the core persistent-store filesystem/framework option.
- Configure default dmesg capture size through `PSTORE_DEFAULT_KMSG_BYTES`.
- Enable optional deflate compression with `PSTORE_COMPRESS`.
- Configure console, pmsg, and ftrace pstore frontends.
- Select dependencies for `PSTORE_RAM`, `PSTORE_ZONE`, and `PSTORE_BLK`.
- Provide pstore/blk defaults for target block device, kmsg size, max reason, pmsg size, console size, and ftrace size.

## Key Interfaces
- `PSTORE` builds the core `pstore.o` code.
- `PSTORE_RAM` builds the `ramoops` backend and selects Reed-Solomon ECC helpers.
- `PSTORE_ZONE` builds the common zone manager used by pstore/blk.
- `PSTORE_BLK` enables persistent storage on block devices and selects `PSTORE_ZONE`.

## Important Behavior
Many pstore/blk sizing options are specified in KB and must be multiples of 4 KB in the runtime validation code. Module parameters can override Kconfig defaults, and the help text explicitly documents that module parameters have priority.

## Cross-File Interactions
The options drive compilation in `fs/pstore/Makefile` and compile-time guards in `platform.c`, `pmsg.c`, `ftrace.c`, `ram.c`, `ram_core.c`, `zone.c`, and `blk.c`.
