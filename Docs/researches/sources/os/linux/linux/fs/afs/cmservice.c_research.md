# File Research: sources/os/linux/linux/fs/afs/cmservice.c

Purpose: implements incoming AFS/YFS cache-manager RxRPC service dispatch, unmarshalling, callback break execution, probes, callback-state reset, and capability replies.

Key interfaces:
- `afs_cm_incoming_call()`: assigns call type based on operation ID and service.
- Call types for `CB.CallBack`, `CB.InitCallBackState`, `CB.InitCallBackState3`, `CB.Probe`, `CB.ProbeUuid`, `CB.TellMeAboutYourself`, and `YFSCB.CallBack`.

Implementation notes:
- Callback calls are executed in workqueue handlers; callback breaks are performed before sending the reply to maintain server cache-coherency ordering.
- Classic `CB.CallBack` unmarshals a bounded FID array (`AFSCBMAX`), discards matching callback records, and verifies call state before reply.
- YFS callback unmarshalling supports wider YFS FID layout and `YFSCBMAX`.
- Init callback state calls clear server callback state.
- InitCallBackState3 and ProbeUuid decode UUIDs from 11 XDR words; ProbeUuid aborts if the UUID does not match the client UUID.
- TellMeAboutYourself replies with client UUID and `AFS_CAP_ERROR_TRANSLATION`.

Dependencies:
- AFS call extraction helpers, RxRPC abort/reply helpers, callback break code, YFS protocol structs, operation ID constants.

Edge cases:
- Callback FID count over protocol max returns protocol error.
- Classic callback count must match FID count unless zero.
- Unsupported incoming operation IDs return false to dispatch.
