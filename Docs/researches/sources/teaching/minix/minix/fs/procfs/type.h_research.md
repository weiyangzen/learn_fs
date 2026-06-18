# File Research: sources/teaching/minix/minix/fs/procfs/type.h

`type.h` defines ProcFS internal data types and documents how `struct file` entries map onto VTreeFS indexes and callback data. `data_t` is an opaque pointer-sized value. `struct load` stores tick count and process-load ticks for load-average calculation.

`struct file` contains a name, mode, and custom data pointer. For static regular files, `data` points to a `void (*)(void)` generator. For static directories, it points to another `struct file` array. For PID dynamic files, it points to a `void (*)(int slot)` generator.

The long comment explains VTreeFS identity rules: PID directories use slot numbers as indexes and PIDs as callback data; PID files use their array index; service files use RS slot indexes; static files/directories use `NO_INDEX` and callback data for generator dispatch. These rules are central to stable getdents behavior and safe regeneration under process churn.
