# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrossNt.h

## Purpose

`CrossNt.h` is the public include for the CrossNt compatibility layer, providing NT-version probing, module/symbol lookup, runtime-resolved kernel helper pointers, and old-NT compatibility shims.

## Main Contents

- Includes NT kernel headers, `ntddk_ex.h`, `rwlock.h`, optionally `ilock.h`, plus `misc.h` and `tools.h`.
- Declares:
  - `CrNtInit`
  - `CrNtGetCPUGen`
  - `CrNtGetModuleBase`
  - `CrNtFindModuleBaseByPtr`
  - `CrNtGetProcAddress`
  - `CrNtSkipImportStub`
- Declares runtime-resolved pointers:
  - `CrNtPsGetVersion`
  - `CrNtNtQuerySystemInformation`
- Exposes global OS/module state:
  - `MajorVersion`, `MinorVersion`, `BuildNumber`, `SPVersion`
  - `g_hNtosKrnl`, `g_hHal`
  - `g_KeNumberProcessors`
- Defines Windows version predicates and numeric IDs.
- In debug builds, remaps `strlen` and `strcmp` to CrossNt implementations for NT 3.51 compatibility.
- Defines `CROSSNT_DECL_API` and includes `CrNtDecl.h` plus `CrNtStubs.h` to emit the external function pointer declarations.

## Integration Notes

This header centralizes the portability contract for code that must run across old NT versions and ReactOS-like environments. It must be included in C++ contexts but wraps exports in `extern "C"`.

## Risks And Edge Cases

- The header exposes global state and macro predicates instead of encapsulated helpers.
- Version predicates are exact comparisons and can misclassify newer systems unless `WinVer_IsdNETp` is used.
- Debug-only `strlen`/`strcmp` remapping can surprise code included after this header.
