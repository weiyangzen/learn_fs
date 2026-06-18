# File Research: sources/os/linux/linux-stable/fs/gfs2/lock_dlm.c

Implements the `lock_dlm` clustered lock manager backend for GFS2. It translates GFS2 glock states and flags into DLM lock modes/flags, handles DLM AST/BAST callbacks, records lock timing statistics, and coordinates cluster journal recovery through DLM lockspace callbacks.

Key entry points are exposed through `gfs2_dlm_ops`: `gdlm_mount`, `gdlm_first_done`, `gdlm_recovery_result`, `gdlm_unmount`, `gdlm_put_lock`, `gdlm_lock`, and `gdlm_cancel`.

Important behavior:
- `gdlm_lock()` builds DLM resource names from glock type/number, computes conversion flags, tracks blocking requests, retries `-EBUSY`, and submits `dlm_lock()`.
- `gdlm_ast()` maps DLM completion statuses to GFS2 lock outcomes, clears initial lock state on first success, handles unlock completion by freeing dead glocks, and clears invalid LVBs.
- `gdlm_bast()` maps DLM blocking callback modes back to GFS2 callback states for demotion pressure.
- `gdlm_put_lock()` either skips unlock on lockspace teardown when safe or sends `dlm_unlock()` while preserving LVB updates for exclusive locks.
- Recovery uses `control_lock` and `mounted_lock` plus a control-lock LVB containing a generation number and jid bitmap.
- `gfs2_control_func()` propagates DLM failed-slot notifications into LVB bits, starts `gfs2_recover_set()` for pending journals, clears recovered bits, and thaws glocks when all recovery for the generation is complete.
- `control_mount()` distinguishes first mounter, normal mounter, and spectator cases; first mounters recover all journals before allowing others to proceed.
- DLM callbacks `gdlm_recover_prep`, `gdlm_recover_slot`, and `gdlm_recover_done` maintain generation and failed-journal arrays under `ls_recover_spin`.

Dependencies include Linux DLM APIs, GFS2 glock core, recovery workqueues, lock value blocks, and filesystem mount arguments. The main correctness risks are generation ordering, LVB bitmap consistency, lockspace teardown races, and preserving first-mounter recovery semantics.
