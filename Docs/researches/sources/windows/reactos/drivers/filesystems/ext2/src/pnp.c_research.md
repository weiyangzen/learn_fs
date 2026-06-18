# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/pnp.c

This file handles Ext2 filesystem Plug and Play IRPs for Windows 2000+ builds.

`Ext2Pnp` validates the IRP context and VCB, forces wait behavior, dispatches minor functions, and forwards unhandled PnP IRPs to the lower storage device. Handled paths usually consume the IRP and set `IrpContext->Irp = NULL`.

`Ext2PnpQueryRemove` waits for lazy writer activity, flushes files and volume state, locks the VCB, purges cached volume state, sends the query down synchronously with a completion event, and calls `Ext2CheckDismount` on success.

`Ext2PnpRemove` and `Ext2PnpSurpriseRemove` lock the VCB, forward the IRP, purge volume cache, check dismount, and set `VCB_DEVICE_REMOVED`. `Ext2PnpCancelRemove` unlocks the VCB and forwards the cancel-remove IRP.

Research notes: PnP forwarding depends on careful ownership of `IrpContext->Irp`. Error paths after failed VCB validation still rely on `Vcb->TargetDeviceObject` in the final forwarding path, so corrupted/non-VCB device extensions are risky.
