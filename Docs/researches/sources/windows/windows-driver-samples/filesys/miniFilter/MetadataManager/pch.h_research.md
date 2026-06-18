# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/pch.h

## Purpose

`pch.h` is the precompiled-header include file for the MetadataManager minifilter sample.

It centralizes warning policy and common includes for all source files in the project.

## Include Guard

The file uses:

```c
#ifndef __FMM_PCH_H__
#define __FMM_PCH_H__
...
#endif __FMM_PCH_H__
```

The trailing token after `#endif` is nonstandard style but accepted by the Windows compiler environment this sample targets.

## Warning Policy

The file promotes several warnings to errors:

- `4100`: unreferenced formal parameter.
- `4101`: unreferenced local variable.
- `4061`: missing enumeration value in switch.
- `4505`: unreferenced local function.

This forces the sample to explicitly mark unused parameters and keep switch/function hygiene tight.

## Included Headers

The common include set is:

- `<fltKernel.h>`: Filter Manager and kernel APIs.
- `<dontuse.h>`: WDK header that discourages unsafe APIs.
- `<suppress.h>`: WDK suppression support.
- `"MetadataManagerStruc.h"`: structures/constants/debug macros.
- `"MetadataManagerProc.h"`: function prototypes and resource helpers.

## Research Notes

This file establishes the build environment for the minifilter sample. All project C files include it, so its warning policy and header order affect the entire MetadataManager sample.
