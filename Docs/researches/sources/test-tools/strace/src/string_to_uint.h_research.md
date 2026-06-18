# sources/test-tools/strace/src/string_to_uint.h

Purpose: declares the generic parser and supplies typed wrappers for common unsigned-limit command-line conversions.

Important APIs/types/functions: `string_to_uint_ex`, `string_to_uint_upto`, `string_to_uint`, `string_to_ulong`, `string_to_kulong`, and `string_to_ulonglong`.

Control flow: inline wrappers delegate to `string_to_uint_ex` with fixed maximums: `INT_MAX`, `LONG_MAX`, signed kernel-long maximum, or `LLONG_MAX`.

State and persistence behavior: stateless inline conversion helpers.

Dependencies and integration points: includes `<limits.h>` and `kernel_types.h`; used widely by option parsers and procfs numeric parsing.

Risks: wrappers return signed types and use `-1` for invalid input; callers must treat zero/positive values according to their own semantic constraints.

Test signals: compile for different kernel word sizes, parse max boundary values, and verify callers reject `0` where positive-only semantics are required.
