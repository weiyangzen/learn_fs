# sources/test-tools/fio/debug.c

Purpose: Provides the debug print implementation when fio is built with `FIO_INC_DEBUG`.

Important APIs/functions: Defines `__dprint(int type, const char *str, ...)`, which asserts the debug channel is valid and forwards the formatted varargs to `log_prevalist()`.

Control flow: The `dprint` macro in `debug.h` checks the runtime bitmask, then calls `__dprint()` only for enabled categories. This file is compiled to real behavior only under `FIO_INC_DEBUG`.

State/persistence: No local state. It consumes global debug mask state declared elsewhere and writes to fio logging.

Dependencies/integration: Includes `debug.h` and `log.h`. Every fio subsystem using `dprint()` depends on this contract in debug builds.

Risks: The assert catches invalid channel numbers only in assert-enabled builds. Format-string safety is declared in the header, not here.

Test signals: Debug builds should verify each channel emits when enabled and remains silent when disabled; non-debug builds should compile away calls.
