# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icharout.h

Interface to character outline and cache setup helpers in `zcharout.c`.

Key declarations:
- `zchar_exec_char_proc`
- `zchar_get_metrics` and `zchar_get_metrics2`
- `zchar_get_CDevProc`
- `zchar_set_cache`
- `zchar_charstring_data`
- `zchar_enumerate_glyph`

It defines `metrics_present` to distinguish no metrics, width-only metrics, and side-bearing-plus-width metrics.
