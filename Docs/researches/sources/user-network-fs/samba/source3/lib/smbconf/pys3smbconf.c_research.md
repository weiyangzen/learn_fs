# sources/user-network-fs/samba/source3/lib/smbconf/pys3smbconf.c

## Purpose
This file implements the Python extension module for source3-specific smbconf initialization. It creates Python `SMBConf` objects backed by Samba's source3 registry or generic smbconf backends.

## Important APIs, Types, And Functions
The module exports `init_reg(path)` and `init(source)`. `py_new_SMBConf()` imports and calls `samba.smbconf.SMBConf` to create the common Python wrapper object. `py_raise_SMBConfError()` delegates error creation to `samba.smbconf._smbconf_error`. `py_init_reg()` accepts `None` or a registry path and calls `smbconf_init_reg()`. `py_init_str()` accepts a backend source string and calls `smbconf_init()`.

## Control Flow
Each initializer parses Python args, imports `samba.smbconf`, creates an object, extracts its talloc context from `py_SMBConf_Object`, initializes a C `smbconf_ctx`, stores it in the Python object, and returns it. On smbconf errors it raises the common Python exception and clears temporary references.

## State And Persistence
The module stores no global mutable state. Returned Python objects own a C smbconf context, which may read or write registry-backed configuration depending on backend operations.

## Dependencies And Integration Points
It depends on Python C API, Samba py3 compatibility, common `lib/smbconf/pysmbconf.h`, source3 `smbconf_reg.h`, and `smbconf_init.h`. It bridges `samba.samba3.smbconf` module users to C backends.

## Risks And Test Signals
Risks include Python reference leaks on error paths, assuming object layout from the common module, type parsing (`z` for nullable registry path, `s` for non-null source), and exception creation failure. Tests should import the module, call `init_reg(None)`, call `init("registry:")` and `init("file:/path")`, verify exceptions for invalid sources, and run under Python leak/debug builds if available.
