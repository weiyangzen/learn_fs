# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.c

Builds configuration-dependent interpreter tables from generated `gconf.h`.

Defines:
- `gs_main_instance_init_values`
- `gs_init_file_array`
- `gs_emulator_name_array`
- function type table and count
- `op_defs_all` and `op_def_count`
- plugin instantiation table

This is generated-configuration glue. It binds configured initialization files, emulators, function builders, operators, and plugins into the interpreter.
