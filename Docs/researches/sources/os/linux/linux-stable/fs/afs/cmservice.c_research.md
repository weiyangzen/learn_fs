# File Research: sources/os/linux/linux-stable/fs/afs/cmservice.c

This file implements the server-to-client AFS/YFS cache-manager RPC service.

Major responsibilities:
- Routes incoming callback service calls by operation ID.
- Defines call types for callback break, callback-state initialization, probe, probe-UUID, capabilities, and YFS callback break.
- Unmarshals incoming XDR request data in resumable stages.
- Breaks callbacks before replying to preserve cache coherency.
- Sends empty, simple, or abort replies through RxRPC helper functions.
- Cleans up per-call buffers in the call destructor.

Supported operations:
- `CB.CallBack` unmarshals classic AFS FID arrays and callback arrays, validates count limits, and schedules callback breaks.
- `CB.InitCallBackState` discards request data and reinitializes all callback promises associated with the server.
- `CB.InitCallBackState3` unmarshals a UUID and checks it against the server UUID.
- `CB.Probe` replies empty to indicate the cache manager is alive.
- `CB.ProbeUuid` compares the supplied UUID against the client UUID and aborts negatively on mismatch.
- `CB.TellMeAboutYourself` replies with interface UUID and capabilities, including error translation.
- `YFSCB.CallBack` unmarshals 64-bit YFS FIDs and queues the same callback-break work path.

Unmarshalling model:
- Each deliver function uses `call->unmarshall` state to support partial network delivery.
- Temporary extraction, fixed-size buffer extraction, discard iterators, and final call-state checks are used consistently.
- Protocol count mismatches return protocol errors rather than processing malformed callback arrays.

Work handlers:
- Callback break work calls `afs_break_callbacks()` while the server is still delaying visibility.
- Init callback state work calls `afs_init_callback_state()`.
- Probe and tell-me work send replies and drop the call reference.
