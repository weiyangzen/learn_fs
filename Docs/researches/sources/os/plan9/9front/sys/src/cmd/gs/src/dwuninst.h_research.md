# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwuninst.h

## Role
Resource identifier header for the Ghostscript Win32 uninstaller.

## Contents
- Defines menu/dialog/control IDs for uninstall resources, including dialog ID, icon, progress text, done/press-ok controls, and text labels.

## Important Interfaces
- IDs such as `ID_UNINSTGS`, `ID_UNINST`, `IDD_UNSET`, `IDC_GSICON`, `IDC_PROG`, `IDC_DONE`, `IDC_PRESSOK`, `IDC_T1`, `IDC_T2`.

## Dependencies And Coupling
- Paired with resource scripts and `dwuninst.cpp`.

## Risks And Notes
- Minimal resource contract; duplicate value aliases are intentional (`IDC_DONE`/`IDC_PRESSOK`).

## Filesystem Relevance
None directly.
