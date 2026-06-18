# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.c

Implements utilities for extracting typed parameters from dictionaries.

Key behavior:
- Boolean, integer/null, integer, unsigned integer, and float getters apply defaults, type checks, range checks, and missing-key behavior.
- Integer getters accept integral real values for compatibility with Fontographer-generated output.
- Integer array helpers support exact-length, max-length, and custom under/over error variants.
- Float array helpers handle array-like refs, optional defaults, and exact/max length behavior.
- `dict_proc_param` validates procedures or supplies invalid/empty defaults.
- `dict_matrix_param` reads a matrix from a dictionary value.
- `dict_uid_param` extracts XUID in Level 2 mode or UniqueID otherwise, allocating XUID value arrays and treating UniqueID 0 as invalid for Fontographer compatibility.
- `dict_check_uid_param` verifies a dictionary UID matches an existing UID.

Research notes:
- These helpers centralize PostScript dictionary parameter validation and defaulting.
- Return conventions distinguish found, defaulted, null, and error cases.
