# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfparam.c

Implements parameter get/put support for CCITTFax filters. It defines the mapping between PostScript/PDF parameter names and `stream_CF_state` fields.

` s_CF_get_params` writes all or only non-default parameters. `s_CF_put_params` reads a parameter list into a copy of the state, validates ranges for `K`, `Columns`, `Rows`, `DamagedRowsBeforeError`, and power-of-two `DecodedByteAlign`, then commits the copy on success.

Dependencies include Ghostscript parameter APIs, `scf.h` for maximum width, and `scfx.h` for state layout.

This is stream parameter validation, not filesystem code.
