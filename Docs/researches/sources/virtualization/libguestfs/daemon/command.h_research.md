# File Research: sources/virtualization/libguestfs/daemon/command.h

Header for daemon external-command helpers.

Key points:
- Defines convenience macros `command`, `commandr`, `commandv`, and `commandrv`.
- Declares command flags and fd mask.
- Declares the four implementation functions.
- Variadic declarations use `__attribute__((sentinel))` to enforce null termination.
