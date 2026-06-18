# sources/security-integrity/selinux/dbus/selinux_client.py

## Purpose

`selinux_client.py` is a small client/demo utility for the `org.selinux` D-Bus service. It calls `SELinuxDBus().customized()` and converts `semanage export` text into a Python dictionary.

## Important APIs And Functions

The script imports `dbus`, `dbus.service`, and `SELinuxDBus` from `sepolicy.sedbus`. `convert_customization(buf)` parses newline-separated semanage export records into dictionaries keyed by customization kind. It initializes a dedicated `fcontext-equiv` dictionary and then recognizes `boolean`, `login`, `interface`, `user`, `port`, `node`, `fcontext`, and `module` records.

When run as `__main__`, it creates a D-Bus proxy, calls `customized()`, prints the converted result, and prints any `dbus.DBusException`.

## Control Flow

Parsing is line oriented. Empty lines are skipped. Records with `rec[1] == "-D"` are ignored. For each record, the first token selects the output dictionary and fixed positional fields are used to extract values such as boolean active state, login SELinux user/range, user level/range/role, port protocol, node mask/protocol/type, fcontext type or equivalence, and module enabled state.

## State And Persistence

The script has no persistent state. It builds an in-memory dictionary from server output.

## Dependencies And Integration Points

It depends on `sepolicy.sedbus.SELinuxDBus` and the exact output format of `/usr/sbin/semanage export` as returned by `selinux_server.py`. It integrates with the D-Bus server's `customized` method and can feed higher-level migration or display tools.

## Risks

The parser assumes minimum token counts before indexing `rec[1]`, `rec[2]`, and later positions; malformed or changed semanage output can raise `IndexError`. The `interface` branch writes into `cust_dict["login"]`, which appears suspicious because an `interface` dictionary is initialized by the generic branch but not used there. It uses tuple keys for ports and fcontexts, which may complicate serialization.

## Test Signals

Unit tests should feed representative semanage export lines for each record type, including empty lines and `-D` deletes, and assert the dictionary shape. Negative tests should cover malformed records and the `interface` behavior.
