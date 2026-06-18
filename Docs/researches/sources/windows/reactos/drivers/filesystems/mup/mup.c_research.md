# File Research: sources/windows/reactos/drivers/filesystems/mup/mup.c

This file implements the ReactOS Multi UNC Provider driver. It routes UNC opens to registered network redirectors, maintains known-prefix caching, supports provider registration, broadcasts mailslot opens, and fans out mailslot writes.

Global state includes locks for global data, prefix table, CCB list, and VCB access; provider, prefix, and master-query lists; a Unicode prefix table; a known-prefix timeout; provider count/order flags; DFS enablement; and the MUP device object.

Initialization:
- `MupInitializeData` creates resources/lists and initializes the prefix table.
- `MuppIsDfsEnabled` reads `DisableDfs` under the MUP service key; DFS is attempted unless explicitly disabled.
- `DriverEntry` initializes data, attempts DFS initialization, creates `\Device\Mup`, registers dispatchers, and initializes the VCB.

Provider management:
- Provider order is read from `Control\NetworkProvider\Order`.
- Each provider’s `NetworkProvider\DeviceName` is used to create unregistered provider records.
- `FSCTL_MUP_REGISTER_PROVIDER` registers a redirector, opens its device, stores object references, and inserts it in provider-order order.

Open routing:
- `MupCreate` treats empty root opens as MUP volume opens and named opens as redirected opens.
- `CreateRedirectedFile` first checks the known-prefix table. If a valid prefix is found, `MupRerouteOpen` rewrites the file object name to prepend the provider device path and returns `STATUS_REPARSE`.
- On a cache miss, it sends `IOCTL_REDIR_QUERY_PATH` to registered providers and waits through a master query context. Completion chooses the best provider by success, accepted-prefix length, and provider order, then caches accepted prefixes.

Mailslot handling:
- Mailslot paths are detected before regular redirector resolution.
- `BroadcastOpen` opens the mailslot against every provider that supports mailslots and attaches resulting CCBs under one MUP FCB.
- `MupForwardIoRequest` forwards writes to every CCB associated with the FCB, using lower IRPs and a master I/O context to complete the original IRP when all forwarded writes finish.

I/O forwarding:
- `BuildAndSubmitIrp` constructs lower write IRPs for buffered, direct, or neither I/O devices, copying stack parameters and installing a completion routine.
- Completion frees MDLs/buffers/lower IRPs, dereferences CCBs, and updates the master I/O context.

Cleanup/close:
- `MupCleanup` handles VCB cleanup, provider deregistration/close, and FCB cleanup.
- `MupClose` clears file-object contexts and dereferences VCB/FCB nodes.
- `MupUnload` deletes the MUP device, unloads DFS if enabled, and deletes resources.

Research notes:
- DFS is effectively disabled because `DfsDriverEntry` currently returns `STATUS_NOT_IMPLEMENTED`.
- Known-prefix timeout logic appears inverted in comments versus condition: the code reroutes when `ValidityTimeout < CurrentTime`, which normally means expired.
- Error selection for provider query failures uses `MupOrderedErrorList` to prefer more critical failures.
- The code uses many manual reference-count paths; provider, prefix, FCB, CCB, and master-context lifetimes are central to correctness.
