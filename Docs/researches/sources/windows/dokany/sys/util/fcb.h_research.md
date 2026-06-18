# File Research: sources/windows/dokany/sys/util/fcb.h

Public utility header for Dokan FCB lookup, release, garbage collection, AVL callbacks, and rename support.

Key responsibilities:
- Declares special internal filename constants: `g_KeepAliveFileName` and `g_NotificationFileName`.
- Exposes `DokanGetFCB` and `DokanFreeFCB` as the main FCB acquisition/release API.
- Declares garbage-collection lifecycle helpers: start, schedule, cancel, force, and delete.
- Declares AVL table comparison/allocation/free callbacks used by each volume’s FCB table.
- Declares `DokanRenameFcb` for updating table membership after a rename.

Important behavior documented by the header:
- `DokanFreeFCB` decrements `OpenCount` and either deletes or schedules GC when it reaches zero.
- GC start is optional; callers check whether `Vcb->FcbGarbageCollectorThread` remains `NULL`.
- Schedule, cancel, force, and delete operations require the VCB lock; delete also requires the FCB lock and must not be followed by an unlock of the freed FCB.
- `DokanCancelFcbGarbageCollection` always deletes or takes ownership of `NewFileName->Buffer`.
- `DokanRenameFcb` requires VCB and FCB acquisition before the call.

Dependencies:
- Includes `../dokan.h` for core Dokan types and Windows kernel declarations.
- Function contracts align with the `fcb.c` implementation and volume setup in `fscontrol.c`.

Notable risks:
- The comments encode important ownership and locking rules; violating them can cause use-after-free, leaked filename buffers, or recursive lock deadlocks.
- A typo in the rename comment says “priore,” but the intended contract is clear.
