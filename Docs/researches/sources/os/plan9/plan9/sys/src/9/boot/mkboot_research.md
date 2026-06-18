# File Research: sources/os/plan9/plan9/sys/src/9/boot/mkboot

RC script that generates boot-method C configuration for a kernel config file.

Key behavior:
- Requires one config-file argument.
- Emits C includes and `Method method[]`.
- Uses `../port/mkextract boot` plus `awk` to turn boot section entries into `{ name, configX, connectX, arg }`.
- Emits `cpuflag`, `rootdir`, `bootdisk`, selected boot program, and a generated `main()` that calls the boot program.
- Detects whether bootdir includes `bin/cfs` and emits `int (*cfs)(int) = cache;` or `0`.

This is build-time glue for architecture-specific boot binaries.
