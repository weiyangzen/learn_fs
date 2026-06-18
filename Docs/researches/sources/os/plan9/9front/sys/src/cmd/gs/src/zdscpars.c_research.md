# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdscpars.c

Bridges Ghostscript PostScript code to Russell Lang’s DSC parser.

Key behavior:
- Defines `.initialize_dsc_parser` and `.parse_dsc_comments`.
- Stores a `CDSC *` parser pointer in a client dictionary under `DSC_struct`, wrapped in a GC-managed `dsc_data_t` with finalizer.
- Ignores parser errors by returning `CDSC_OK` from the error handler and mapping negative scan results to NOP.
- Skips data/binary block comments that would otherwise cause the C parser to consume external data.
- Maps supported DSC comment codes to PostScript names and writes selected values into the supplied DSC dictionary.
- Handles header/EPSF, creator, creation date, title, for, bounding boxes, pages, orientation, viewing orientation, and EOF/NOP.

Dependencies:
- Uses `dscparse.h`, dictionary parameter-list writing, interpreter struct allocation/finalization, and PostScript name creation.

Research notes:
- This file is intentionally a narrow bridge; higher-level DSC interpretation is delegated to `gs_dscp.ps`.
