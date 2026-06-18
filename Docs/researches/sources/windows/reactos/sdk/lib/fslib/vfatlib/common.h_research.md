# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.h

Declares shared VFAT formatting helpers.

Key elements:
- `GetShiftCount`
- `CalcVolumeSerialNumber`
- `FatWipeSectors`

Dependencies:
- Requires ReactOS types and `PFORMAT_CONTEXT`, normally supplied by `vfatlib.h`.

Research notes:
- This header is included by `vfatlib.h`, making helpers available to `fat12.c`, `fat16.c`, and `fat32.c`.
