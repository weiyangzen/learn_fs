# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.c

This file implements ISAKMP attribute encoding and iteration helpers.

Key responsibilities:
- Encodes basic attributes where the value is carried directly in the length/value field.
- Encodes variable-length attributes with explicit data bytes.
- Iterates over a buffer of ISAKMP attributes and invokes a callback per attribute.
- Looks up named configuration constants and writes them as attributes.

Important functions:
- `attribute_set_basic()`: writes an attribute with the ISAKMP basic format bit set.
- `attribute_set_var()`: writes a variable-length attribute and copies payload bytes.
- `attribute_map()`: safely walks an attribute area, handling basic and variable formats.
- `attribute_set_constant()`: reads a config tag, maps its string to a constant value, and emits a basic attribute.

Dependencies:
- Generated ISAKMP field access macros from `isakmp.h`.
- Config lookup via `conf_get_str`.
- Constant mapping via `constant_value`.
- Logging for missing config values.

Research notes:
- `attribute_map()` performs bounds checks before invoking callbacks, making it central to safe transform/proposal parsing.
