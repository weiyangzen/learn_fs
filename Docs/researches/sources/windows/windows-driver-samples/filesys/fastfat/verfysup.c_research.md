# File Research: sources/windows/windows-driver-samples/filesys/fastfat/verfysup.c

## Role

`verfysup.c` implements FastFAT volume and file verification support. It handles removable-media verification, stale FCB/DCB validation, dirty/clean volume marking, deferred clean-volume work, write-protection checks, and verify-required recovery flow.

## Key Routines

- `FatMarkFcbCondition`: marks one FCB/DCB or a subtree as `FcbGood`, `FcbBad`, or `FcbNeedsToBeVerified`, updating Fast I/O state and resetting cached allocation/dirent hints when needed.
- `FatMarkDevForVerifyIfVcbMounted`: sets `DO_VERIFY_VOLUME` on the real device only if the VCB’s VPB is still mounted on that device.
- `FatVerifyVcb`: checks `DO_VERIFY_VOLUME`, handles create requests against unmounted volumes, sets hard-error verify device, and delegates state checks to `FatQuickVerifyVcb`.
- `FatVerifyFcb`: rejects dismounted volumes, tolerates deleted-file cleanup edge cases, quick-verifies the VCB, and revalidates `FcbNeedsToBeVerified` objects by walking ancestors.
- `FatDeferredCleanVolume` and `FatCleanVolumeDpc`: schedule and execute delayed clean-volume marking once dirty cached data has drained, with safeguards for racing volume teardown.
- `FatMarkVolume`: writes FAT dirty/clean state to the boot sector, FAT dirty-bit entry, and FAT32 FSInfo sector when applicable.
- `FatFspMarkVolumeDirtyWithRecover`: marks a volume dirty with surface-test request after paging I/O media errors and then completes or signals the original request.
- `FatCheckDirtyBit`: reads the boot sector dirty bit at mount/verify time and updates `VCB_STATE_FLAG_MOUNTED_DIRTY`.
- `FatVerifyOperationIsLegal`: blocks most operations after cleanup has completed, while permitting paging I/O, close, query/set information, and MDL complete cases.
- `FatResetFcb`: clears cached MCB mapping and allocation-size hints, except for real paging files where losing mapping information would be unsafe.
- `FatDetermineAndMarkFcbCondition`: reloads an FCB’s directory entry and compares short name, file size, first cluster, and attributes to decide whether the in-memory object still matches disk.
- `FatQuickVerifyVcb`: raises the right status for verify-required, not-mounted, bad, dismounted, and write-protected states.
- `FatPerformVerify`: invokes `IoVerifyVolume`, reconciles result with VCB state, may dismount stale volumes, reparses absolute creates after remount, and reposts the IRP.

## Important Mechanics

The verification model separates volume validity from file identity. A VCB can be good, not mounted, or bad, while individual FCB/DCB records can require revalidation after media changes or power transitions.

Dirty marking is compatibility-oriented. `FatMarkVolume` updates both the boot-sector dirty bit and FAT dirty-bit entry, and also refreshes FAT32 FSInfo free-cluster hints when marking clean. It bypasses FAT12 and write-protected media.

Paging files receive special treatment. Real paging files on non-removable media are kept good and retain MCB mappings because invalidating those mappings could crash the system. ReadyBoost-style paging files on removable media are allowed to reverify.

## Dependencies And Coupling

This file is tightly coupled to the mount/verify path, cache manager, VPB/device verification flags, boot-sector format, FAT allocation support, directory-entry lookup, FCB tree traversal, and exception-based FastFAT request processing.
