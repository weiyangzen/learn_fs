# sources/sync-backup/rsync/chmod.c

Purpose: parses and applies rsync's `--chmod` transformation rules.

Important APIs/types/functions: `struct chmod_mode_struct`; public `parse_chmod()`, `tweak_mode()`, `free_chmod_mode()`; helpers `mode_dest_special_bits()` and `mode_copy_bits()`.

Control flow: `parse_chmod()` is a state machine for symbolic and octal modes, supporting `D`/`F` directory/file filters, `u/g/o/a`, `+/-/=`, `r/w/x/X/s/t`, and permission-copy forms. It appends parsed operations to a linked list. `tweak_mode()` applies each operation to a mode while preserving non-permission file type bits.

State and persistence: parsed linked list is heap state owned by caller. Uses global `orig_umask` for unspecified symbolic targets.

Dependencies/integration: used by options/receiver metadata application; relies on rsync mode macros from `rsync.h`.

Risks: parser edge cases can silently reject complex chmod syntax by returning NULL. `X` depends on original executable bits or directory type.

Test signals: chmod-specific tests and `t_chmod_secure` helper in Makefile cover parser/application behavior.
