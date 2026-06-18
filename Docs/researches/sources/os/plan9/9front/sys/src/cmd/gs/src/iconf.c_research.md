# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.c

Builds configuration-dependent interpreter tables.

Key points:
- Defines `gs_main_instance_init_values` from default initializer macros.
- Uses `gconf.h` macro expansions to build init `.ps` filename refs and emulator-name refs.
- Declares and builds the function type table from configured function builders.
- Declares and builds the operator definition table, always including `interp_op_defs`.
- Declares and builds the plugin instantiation table from configured plugins.
- The string ref arrays use foreign readonly strings and are terminated by a null string entry.

Research notes:
- This is generated-configuration glue driven by `gconf.h`.
- `iconfig.c` in this group has the same content under a different filename.
