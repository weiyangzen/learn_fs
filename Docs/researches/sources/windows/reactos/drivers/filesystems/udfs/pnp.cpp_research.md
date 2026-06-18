# File Research: sources/windows/reactos/drivers/filesystems/udfs/pnp.cpp

## Role

`pnp.cpp` implements Plug and Play IRP handling for UDF volume device objects, especially query-remove, surprise-remove, and remove-device flows.

## Dispatch Flow

`UDFPnp()` is the top-level dispatch routine. It enters the filesystem, sets top-level IRP state, allocates an IRP context, and calls `UDFCommonPnp()`, using the shared exception filter/handler on errors. The routine contains an unconditional `ASSERT(FALSE)`, suggesting this path may not be expected in normal builds or remains diagnostic.

`UDFCommonPnp()` verifies the target is a VCB, forces blocking mode, and switches on the PnP minor function:

- `IRP_MN_QUERY_REMOVE_DEVICE` -> `UDFPnpQueryRemove()`.
- `IRP_MN_SURPRISE_REMOVAL` -> `UDFPnpSurpriseRemove()`.
- `IRP_MN_REMOVE_DEVICE` -> `UDFPnpRemove()`.
- Other minor functions are skipped down the stack with `IoSkipCurrentIrpStackLocation()` and `IoCallDriver()`.

## Remove Handling

`UDFPnpQueryRemove()` acquires global and VCB resources, closes delayed/system delayed objects, runs `UDFDoDismountSequence()`, stops the eject waiter, forwards the query remove down the device stack with a completion event, and if successful forces dismount through `UDFCheckForDismount()`. It then completes the original IRP.

`UDFPnpRemove()` acquires global and VCB resources, closes delayed objects, clears any volume lock state, forwards the remove down the stack and waits, marks the real device for verify, runs dismount, clears mounted/write-security flags, stops the eject waiter, checks for dismount, releases resources, frees the media-removal buffer, and completes the IRP.

`UDFPnpSurpriseRemove()` follows the same broad structure as remove but is used for unplanned device disappearance. It forwards the surprise-remove IRP first, then marks verify, dismounts, clears mounted/write-security flags, stops the eject waiter, checks for dismount, and completes.

`UDFPnpCompletionRoutine()` signals the supplied event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can finish processing synchronously.

## Dependencies

The file depends on VCB state, delayed close, dismount sequencing, eject waiter control, `UDFCheckForDismount()`, global/VCB resource ordering, IRP stack forwarding helpers, and lower storage-stack PnP behavior.

## Notable Risks

- `UDFPnp()` asserts false unconditionally, so debug builds will break on any PnP dispatch.
- `UDFPnpQueryRemove()` allocates `Buf` but does not free it in its finally block, unlike remove and surprise-remove paths.
- `UDFPnpRemove()` and `UDFPnpSurpriseRemove()` declare `VcbDeleted` and `VcbAcquired` without explicit initializers before complex control flow, so any early path must set them before finally uses them.
- Cancel-remove support is present only as commented-out code, so query-remove recovery is not implemented here.
