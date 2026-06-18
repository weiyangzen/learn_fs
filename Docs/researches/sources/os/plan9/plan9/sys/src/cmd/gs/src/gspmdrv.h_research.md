# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.h

Defines constants shared by the OS/2 Presentation Manager driver source and resource file.

Key definitions:
- `GSPMDRV_VERSION`
- Menu/dialog command IDs: `IDM_ABOUT`, `IDM_COPY`, `IDD_ABOUT`
- Resource ID: `ID_GSPMDRV`

Integration:
- Included by `gspmdrv.c` and referenced by the OS/2 resource script.

Risk notes:
- Header is platform/resource-specific and has no logic.
