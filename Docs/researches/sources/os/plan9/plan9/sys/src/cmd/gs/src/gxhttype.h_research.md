# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttype.h

Purpose: defines the client-visible halftone type enumeration.

Enum values:
- `ht_type_none`.
- `ht_type_screen` for `setscreen`.
- `ht_type_colorscreen` for `setcolorscreen`.
- `ht_type_spot` for Type 1 halftone dictionaries.
- `ht_type_threshold` for Type 3 threshold dictionaries.
- `ht_type_threshold2` for extended threshold dictionaries with byte strings and 8/16-bit samples.
- `ht_type_multiple` for Type 5 halftone dictionaries.
- `ht_type_multiple_colorscreen` for Type 5 objects derived from Type 2/4 dictionaries.
- `ht_type_client_order` for client-defined `gx_ht_order` creation.

Research notes:
- Used by `gxht.h` and other halftone setup code as the discriminator for halftone parameter unions.
