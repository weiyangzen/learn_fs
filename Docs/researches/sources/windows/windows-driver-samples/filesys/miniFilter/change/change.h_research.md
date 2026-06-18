# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.h

## Purpose

Main internal header for the `change` minifilter sample. It pulls in WDK/context/utility definitions, declares global filter state, and defines debug tracing controls.

## Contents

- Defines `CG_VISTA` as `NTDDI_VERSION >= NTDDI_VISTA`.
- Includes `<fltKernel.h>`, `<suppress.h>`, `context.h`, and `utility.h`.
- Disables the PREfast encoded member function pointer warning for kernel-mode drivers.
- Defines `PFLT_FILTER gFilterInstance`.
- Defines trace categories: routines, operation status, debug, and error.
- Initializes `gTraceFlags` to debug plus error.
- Defines `CG_DBG_PRINT()` wrapper around `DbgPrint`.

## Dependencies And Usage

- Included by both `change.c` and `context.c`.
- `gFilterInstance` is used by context allocation in `context.c` and initialized by `DriverEntry()` in `change.c`.

## Risks And Invariants

- The header defines, rather than declares, `gFilterInstance` and `gTraceFlags`; in stricter modern builds, this can create multiple-definition risk when included by multiple C files. The sample relies on its build environment’s handling.
- Debug output is controlled by a static trace flag initialized at compile time, not by registry configuration.
