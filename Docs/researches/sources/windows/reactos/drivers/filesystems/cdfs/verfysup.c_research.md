# File Research: sources/windows/reactos/drivers/filesystems/cdfs/verfysup.c

Implements volume verification, dismount checks, VCB validation, FCB-operation validation, and VCB dismount initiation for CDFS.

Key entry points:
- `CdPerformVerify()` calls `IoVerifyVolume()`, reconciles the result with the current VCB condition, may trigger dismount, reparses successful top-level creates, or posts the original IRP for retry.
- `CdCheckForDismount()` decides whether to start dismount or delete a VCB when references drop to residual values.
- `CdMarkDevForVerifyIfVcbMounted()` marks the real device for verification only if the VCB's VPB is still mounted on that device.
- `CdVerifyVcb()` checks invalid/dismount state, removable-media change state, verify-required state, and raises appropriate verify/wrong-volume/file-invalid statuses.
- `CdVerifyFcbOperation()` validates per-FCB operations, including cleaned-up file objects, invalid/dismount state, real-device verify state, and wrong-volume handling.
- `CdDismountVcb()` transitions a VCB into dismount-in-progress, drops internal FCB references, purges the volume, drains close queues, swaps or clears VPBs, and deletes the VCB if final references are gone.

Core mechanics:
- Verify skips recursive mount/verify FSCTL deadlocks by posting mount/verify requests instead of calling `IoVerifyVolume()`.
- Removable media verification uses `IOCTL_CDROM_CHECK_VERIFY`, media change count comparison, raw-device status, and device verify flags.
- Create requests against unmounted/dismounting volumes can be forced through verify so name opens are rerouted to the currently mounted volume.
- Dismount first tears down internal references, purges cache/sections, drains closes, then handles VPB ownership under the VPB spin lock.
- If outstanding references remain, `CdDismountVcb()` swaps in the preallocated `SwapVpb` so the real device can accept a new mount.

Important invariants:
- `CdCheckForDismount()` requires exclusive global CDFS data ownership.
- VCB deletion only occurs after both VCB references and VPB references reach the expected final counts.
- Dismount may leave the VCB alive if user/file/VPB references remain.
- Fast I/O validation returns `FALSE` instead of raising when no IRP context is present.

Filesystem relevance:
- This file controls media-change detection, wrong-volume handling, create reparsing after remount, forced dismount, and safe volume deletion.

Notable risks:
- VPB swapping and final-reference logic are delicate and depend on holding the correct locks.
- Media-change count is intentionally updated only after an actual verify completes, not when a possible change is detected.
- Operations on cleaned-up file objects are mostly rejected, with narrow exceptions for paging I/O, close, query information, and MDL read completion.
