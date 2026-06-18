# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserrors.h

## Role

`gserrors.h` defines core Ghostscript library error code constants.

## Error Convention

Functions that may fail return non-negative values for success and negative values for errors. The file uses integer macros rather than an enum to avoid casting.

## Defined Errors

Includes common PostScript/Ghostscript errors such as:

- `gs_error_unknownerror`
- `gs_error_interrupt`
- `gs_error_invalidaccess`
- `gs_error_invalidfileaccess`
- `gs_error_invalidfont`
- `gs_error_ioerror`
- `gs_error_limitcheck`
- `gs_error_nocurrentpoint`
- `gs_error_rangecheck`
- `gs_error_typecheck`
- `gs_error_undefined`
- `gs_error_undefinedfilename`
- `gs_error_undefinedresult`
- `gs_error_VMerror`
- `gs_error_unregistered`

Also defines special internal/fatal values:

- `gs_error_hit_detected`
- `gs_error_Fatal`

## Dependencies

None beyond C preprocessing.

## Risks

Because these are macros, they have no type safety. Callers must preserve the convention that success is non-negative and errors are negative.
