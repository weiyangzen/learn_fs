# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddipropdefs.h

This header defines DDI property implementation types, property operation enums, property flags, encoded property handle operations, return codes, common property names, and debugging hooks.

`ddi_prop_op_t` describes property operation mode: length only, length plus caller buffer, length plus allocated buffer, or existence check. `ddi_prop_t` is the in-kernel software property node, storing next pointer, matching dev_t, property name, flags, length, and value pointer. `ddi_prop_list_t` wraps a reference-counted list.

Encoded property access is represented by `prop_handle_t` and `prop_handle_ops_t`, with ops for int, string, byte, and int64 data. Command enum values request encoded size, decoded size, decode, encode, or skip. Result values distinguish encoding/decoding error, end of data, and success/positive size.

The file defines IEEE 1275 property cell helpers, property handle flags, property return codes, and a large set of property flags: don't pass to parent, can sleep, system-defined, not PROM, don't sleep, stack create, undefine, hardware-defined, typed int/string/byte/composite/int64, LDI dev_t wildcard, unbound DLPI2 lookup, typed consumer expansion, dynamic driver prop_op lookup, and rootnex global lookup.

Common dev_t/major constants include `DDI_DEV_T_NONE`, `DDI_DEV_T_ANY`, `DDI_MAJOR_T_UNKNOWN`, and `DDI_MAJOR_T_NONE`. Common root properties include `relative-addressing` and `generic-addressing`.

It declares `ddi_prop_search_common()` and optional property debugging support under `DDI_PROP_DEBUG`.

Research notes:
- This is private to property implementation, despite being included by public-adjacent DDI code.
- Typed property flags and older untyped lookup compatibility are intertwined.
- Property values are stored by reference, so allocation/free ownership matters.
