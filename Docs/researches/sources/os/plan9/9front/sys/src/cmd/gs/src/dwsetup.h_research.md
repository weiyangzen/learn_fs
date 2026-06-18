# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.h

## Role
Resource identifier header for the Ghostscript Win32 setup program.

## Contents
- Defines dialog IDs, resource IDs, string IDs, and control IDs used by `dwsetup.cpp` and resources.
- Includes IDs for main dialog controls: target directory/group, browse buttons, readme, install fonts, text log, install button, all-users checkbox, copyright, and CJK fonts.

## Important Interfaces
- IDs such as `IDD_MAIN`, `IDD_TEXTWIN`, `IDC_TARGET_DIR`, `IDC_INSTALL`, `IDC_INSTALL_FONTS`, `IDC_ALLUSERS`, `IDC_CJK_FONTS`.

## Dependencies And Coupling
- Paired with resource scripts and `dwsetup.cpp`.

## Risks And Notes
- Values must stay synchronized with `.rc` resources.

## Filesystem Relevance
None directly.
