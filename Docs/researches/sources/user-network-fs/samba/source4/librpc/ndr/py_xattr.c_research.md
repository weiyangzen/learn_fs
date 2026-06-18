# sources/user-network-fs/samba/source4/librpc/ndr/py_xattr.c

## Purpose

`py_xattr.c` patches generated Python bindings for `xattr_NTACL` with a debug dump method.

## Important APIs And Types

`PyType_AddMethods()` injects methods into a Python type. `ntacl_print_debug_helper()` implements an `ndr_print` callback that formats indented lines to stdout. `py_ntacl_print()` allocates an `ndr_print`, sets the print callback, and invokes `ndr_print_xattr_NTACL(pr, "file", ntacl)`. `PY_NTACL_PATCH` maps to `py_xattr_NTACL_patch`.

## Control Flow And State

Calling `.dump()` on a Python NTACL object prints the NDR representation to stdout and returns `None`. It allocates a temporary talloc context and frees it before returning. It does not mutate the ACL.

## Dependencies And Integration Points

It depends on Python C API, pytalloc, generated xattr NTACL NDR print functions, and Samba's NDR print infrastructure. It is primarily a diagnostic hook for Python tests/tools dealing with NT ACL xattrs.

## Risks

The method writes directly to stdout, which can pollute test output and is not structured logging. `vasprintf()` failures silently skip a line. Dumping ACLs may expose sensitive security descriptor information.

## Test Signals

Tests should call `.dump()` on a minimal and populated NTACL object, capture stdout, and verify no mutation or leaks occur on repeated calls.
