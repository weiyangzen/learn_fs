# sources/user-network-fs/samba/source3/modules/getdate.h

## Purpose
Small portability header for the `get_date()` natural-language date parser. It exposes the single parser API while handling older C prototype conventions and platform-dependent time includes.

## APIs, Types, And Control Flow
The only exported symbol is `time_t get_date(const char *p, const time_t *now)`, declared through the `PARAMS` macro for compatibility with pre-ANSI builds. Include control flow selects `config.h`, VMS `types.h`, or POSIX `sys/types.h`, `sys/time.h`, and `time.h` based on `TIME_WITH_SYS_TIME` and `HAVE_SYS_TIME_H`.

## State, Dependencies, Integration
The header has no state or persistence. It depends on Samba or autoconf feature macros and the system time type definitions. It is included by the generated parser implementation and by modules that call `get_date()`, notably the readonly VFS module.

## Risks And Test Signals
The main risk is build portability: incorrect config macros can hide `time_t` or duplicate time declarations on unusual platforms. Tests are compile-time signals: consumers should include this header alone and through `getdate.c`, with and without modern prototypes, and verify the exported function signature remains consistent.
