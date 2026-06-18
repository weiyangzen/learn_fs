# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msio.c

Windows text-window stdio stream substitution.

Key behavior:
- Registers a pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` open procedures when the corresponding C stream is a console.
- Replaces stream processing with callback-based stdin and stdout/stderr handlers using `pgsdll_callback`.
- Marks stream availability as unknown/EOF-like with `*pl = -1`.
- Overrides `fprintf` for supported Windows compilers so console writes go through the Ghostscript DLL callback instead of stdio.

Notable dependencies:
- Ghostscript stream and IODevice interfaces.
- Windows platform declarations from `gp_mswin.h` and callback constants from `gsdll.h`.

Research notes:
- The file contains an MSVC `/MD` workaround to avoid `fprintf` import/export conflicts.
- It assumes `pgsdll_callback` is valid on the callback paths.
