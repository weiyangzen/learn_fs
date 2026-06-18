# sources/user-network-fs/samba/source4/lib/registry/pyregistry.c

## Purpose

`pyregistry.c` exposes a small Python module named `samba.registry` for opening Samba registry contexts and hive keys, mounting hives, applying diffs, manipulating hive values, and converting registry type ids to strings.

## Important APIs, Types, and Functions

The file defines Python types `PyRegistry`, `PyRegistryKey`, and `PyHiveKey`, backed by pytalloc-managed `struct registry_context`, `struct registry_key`, and `struct hive_key` pointers. Registry methods include `get_predefined_key_by_name()`, `get_predefined_key()`, `key_del_abs()`, `diff_apply()`, and `mount_hive()`. Hive-key methods include `del()`, `flush()`, `del_value()`, and `set_value()`. Module-level functions include `open_samba()`, `open_ldb()`, `open_hive()`, `str_regtype()`, and `get_predef_name()`.

## Control Flow

Module initialization readies the pytalloc-backed types, creates the module, and publishes HKEY constants. Constructing `Registry()` opens an empty local registry. `open_hive()` and `open_ldb()` convert Python loadparm and credentials objects to Samba C objects, call the matching C open routine, and return a `HiveKey`. `open_samba()` opens the full local Samba registry. Method wrappers parse Python arguments, call the underlying C registry API, translate `WERROR` failures into Python exceptions, and return stolen talloc objects or `None`.

## State and Persistence Behavior

The Python objects own or steal talloc references to C registry objects. Opening a hive may create or mutate backing LDB files depending on the lower backend. `HiveKey.set_value()` treats `None` data as a delete request; non-`None` bytes are passed as a `DATA_BLOB`. `mount_hive()` can alter the in-memory registry context by attaching a hive under a predefined key and optional elements list.

## Dependencies and Integration Points

The binding integrates Python C API compatibility headers, pytalloc, Samba WERROR-to-Python error helpers, loadparm Python conversion, credentials conversion, tevent context creation, and the registry C library. It is built as `samba/registry.so` by `wscript_build`.

## Risks and Edge Cases

Several wrappers accept optional `session_info` but then set `session_info = NULL`, so Python callers cannot currently pass real session state. `py_open_samba()` declares only two keyword names but parses three optional objects, which makes the credentials keyword contract unclear. `py_mount_hive()` allocates the elements array on `NULL` and does not append a NULL sentinel, so it depends on `reg_mount_hive()` using a known list length or tolerating the caller's layout. Python string/bytes handling for `set_value()` uses `z#`, so embedded NULs are accepted but require the caller to pass bytes-like data correctly.

## Test Signals

Build tests must import `samba.registry`, instantiate `Registry`, open LDB and REGF hives through `open_hive()`, set and delete hive values, apply a diff file, mount a hive under an HKEY constant, and check WERROR exception translation on missing keys and invalid type conversions.

Source-read signal: reviewed complete local file (494 lines).
