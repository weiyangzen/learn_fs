# sources/user-network-fs/samba/source4/libnet/py_net_dckeytab.c

## Purpose

`py_net_dckeytab.c` implements a Python extension initializer that injects `export_keytab()` into the existing `samba.net.Net` type. The method exports DC or principal Kerberos keys to a keytab through `libnet_export_keytab()`.

## Important APIs, Types, and Functions

`py_net_export_keytab()` parses `keytab`, optional `samdb`, optional `principal`, and boolean flags `keep_stale_entries`, `only_current_keys`, and `as_for_AS_REQ`; validates optional `samdb` as an LDB object; calls `libnet_export_keytab()` with the current `Net` object's `libnet_context`; and maps NTSTATUS failures to Python exceptions.

`MODULE_INIT_FUNC(dckeytab)` creates a dummy module, imports `samba.net`, obtains the `Net` type, creates a method descriptor, and inserts it into `Net.tp_dict`.

## Control Flow

Importing the `dckeytab` extension mutates the method dictionary of `samba.net.Net`. Calling `export_keytab()` creates a talloc context under the Python object, fills `struct libnet_export_keytab`, invokes the C exporter, frees the context, and returns `None` on success.

## State and Persistence Behavior

The method writes or updates the named keytab file. Options can retain stale entries, restrict to current keys, or simulate AS-REQ key selection behavior used by tests. It may read from a supplied `samdb` or use libnet context defaults depending on exporter behavior.

## Dependencies and Integration Points

Dependencies include Python C API, `py_net.h`, `libnet_export_keytab.h`, pyldb validation, and Samba Python NTSTATUS error helpers. It relies on `samba.net` being importable and on the `Net` type layout declared in `py_net.h`.

## Risks and Edge Cases

The module returns the imported `samba.net` module object rather than the initially created dummy module after successful import, which is intentional-looking but unusual. Method injection mutates an existing type at import time and can fail silently by returning a module with no method if intermediate descriptor creation fails. Exporting keytabs handles sensitive key material; tests must use temporary files and strict permissions.

## Test Signals

Python tests should import `samba.dckeytab`, assert `Net.export_keytab` exists, export to a temporary keytab with different flag combinations, cover invalid `samdb` type handling, and verify failure paths do not leave partial sensitive files where possible.
