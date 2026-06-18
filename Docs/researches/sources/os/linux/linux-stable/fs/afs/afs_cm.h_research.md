# File Research: sources/os/linux/linux-stable/fs/afs/afs_cm.h

This header defines the AFS cache-manager service constants and callback operation IDs.

Major contents:
- Defines `AFS_CM_PORT` as 7001.
- Defines `CM_SERVICE` service ID as 1.
- Enumerates cache-manager RPC operation numbers:
  - `CBCallBack`
  - `CBInitCallBackState`
  - `CBProbe`
  - `CBGetLock`
  - `CBGetCE`
  - `CBGetXStatsVersion`
  - `CBGetXStats`
  - `CBInitCallBackState3`
  - `CBProbeUuid`
  - `CBTellMeAboutYourself`
- Defines `AFS_CAP_ERROR_TRANSLATION`, advertised by callback capability replies.

Usage:
- `cmservice.c` uses these operation numbers to route incoming server-to-client callback RPCs.
- `cm_security.c` uses service identity and capability constants when handling RxRPC/RxGK security challenges and callback appdata.
