# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzline.h

Declares internal line-parameter support.

Key points:
- Includes `gxline.h` for `gx_line_params`.
- Defines `private_st_line_params`, a complex GC descriptor for line parameters.
- The descriptor must avoid following the dash pattern pointer when dash pattern size is zero.
- Declares `gs_currentlineparams` for accessing line parameters from an imager state.

Research notes:
- The main behavior is in `gsline.c`/`gsistate.c`; this header isolates GC and accessor details.
