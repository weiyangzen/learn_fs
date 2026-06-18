# File Research: sources/os/linux/linux/fs/afs/afs_cm.h

Purpose: defines AFS cache-manager service constants and operation IDs.

Key contents:
- `AFS_CM_PORT = 7001`.
- `CM_SERVICE = 1`.
- Cache-manager operation IDs: `CBCallBack`, `CBInitCallBackState`, `CBProbe`, `CBGetLock`, `CBGetCE`, `CBGetXStatsVersion`, `CBGetXStats`, `CBInitCallBackState3`, `CBProbeUuid`, `CBTellMeAboutYourself`.
- `AFS_CAP_ERROR_TRANSLATION`.

Implementation notes:
- Used by incoming cache-manager RPC dispatch and security challenge handling.
