# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/pch.h

## Purpose

Precompiled header for the CDO kernel-mode sample.

## Contents

- Enables warnings as errors for unreferenced parameters, unreferenced locals, missing enum cases in switch statements, and dead functions.
- Includes WDK headers: `<fltKernel.h>`, `<dontuse.h>`, and `<suppress.h>`.
- Includes sample headers: `CdoStruct.h` and `CdoProc.h`.
- Disables the PREfast encoded member function pointer warning as not valid for kernel-mode drivers.

## Dependencies And Usage

- Included by `CdoInit.c` and `CdoOperations.c`.
- Centralizes strict warning policy and internal declarations.

## Risks And Invariants

- The final `#endif __CDO_PCH_H__` includes trailing tokens after `#endif`, which is tolerated by many preprocessors but is stylistically noisy.
- Because warning 4100 is an error, implementations must explicitly mark unused parameters with `UNREFERENCED_PARAMETER`.
