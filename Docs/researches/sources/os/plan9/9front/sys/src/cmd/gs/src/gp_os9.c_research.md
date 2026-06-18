# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os9.c

OS-9/OSK-specific platform routines.

Key behavior:
- Installs a signal handler through `intercept`, setting a global `interrupted` flag for interrupt/quit/FPE.
- Computes realtime from OS-9 `_sysdate` and `_julian`, using a January 1, 1980 base.
- Uses realtime as usertime approximation.
- Stubs persistent cache operations.
- Opens printer output as a pipe or a raw-buffered file; empty printer name returns `NULL`.
- Sets raw-buffered mode through the C library `_RBF` flag.
- Stubs native font enumeration.

Research notes:
- The code references `file->_flag` inside `gp_setmode_binary`, though the parameter is named `pfile`, indicating a likely historical typo or platform macro expectation.
