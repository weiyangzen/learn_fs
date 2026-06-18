# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.c

Top-level VFATX FMIFS-style API.

Key elements:
- `VfatxFormat` opens the target volume, queries geometry and partition information, initializes progress context, and calls `FatxFormat`.
- Rejects `BackwardCompatible == TRUE` as unsupported.
- Builds synthetic partition information for non-fixed media.
- `VfatxChkdsk` is unimplemented but returns success.
- `VfatxUpdateProgress` reports percentage changes through the callback.

Dependencies:
- Uses `FatxFormat` from `fatx.c`.
- Uses ReactOS NDK object/I/O APIs and FMIFS callback codes.

Research notes:
- Unlike `VfatFormat`, this function does not lock/dismount/unlock the volume around formatting.
- `Label` and `ClusterSize` parameters are accepted by signature but unused.
- The unimplemented check path means FATX has formatter support but no real consistency checker here.
