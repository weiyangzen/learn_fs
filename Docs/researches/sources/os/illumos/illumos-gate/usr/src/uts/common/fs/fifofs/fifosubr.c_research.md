# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifosubr.c

## Purpose
Provides support routines and module initialization for FIFOFS, including fifonode/pipe allocation, FIFO shadow vnode management, STREAMS open coordination, connld handling, fast FIFO mode transitions, and reader/writer wakeups.

## Main Responsibilities
- Register and initialize the `fifofs` filesystem module.
- Create kmem caches for named FIFO nodes and anonymous pipe pairs.
- Maintain a hash table mapping real FIFO vnodes to FIFOFS shadow vnodes.
- Allocate and initialize pipe endpoint vnodes.
- Coordinate STREAMS open/close serialization for FIFOs and pipes.
- Handle `connld` by creating and passing a new pipe endpoint.
- Manage FIFO fast-mode buffering and transition to STREAMS mode.
- Wake blocked readers/writers and trigger poll/SIGPOLL notifications.

## Core State
- `fifoalloc[FIFO_HASHSZ]`: hash table of real vnode to fifonode shadows.
- `fifodev`, `fifovfsp`, `fifofstype`: synthetic FIFOFS device/VFS metadata.
- `ftable_lock`: protects FIFO shadow hash table.
- `fino_lock`: protects anonymous pipe inode counter.
- `fnode_cache`: cache for single-fnode FIFO data.
- `pipe_cache`: cache for two-fnode pipe data.
- `fifolock_t`: shared lock/CVs and synchronization state for one FIFO or pipe pair.

## Constructors and Destructors
`fnode_constructor()`:
- Initializes shared fifolock and every embedded fifonode.
- Allocates a vnode for each fnode.
- Initializes counters, destination pointer, stream state, pid/cred fields, wait CV, vnode ops/type/data/flags.
- Handles partial allocation failure by calling destructor.

`fnode_destructor()`:
- Asserts clean state.
- Destroys CVs, invalidates/frees vnodes, destroys shared lock/CV.

`pipe_constructor()`:
- Uses `fnode_constructor()` for two fnodes.
- Sets both vnodes to global FIFOFS VFS/device.
- Cross-links destinations between the two pipe ends.

`pipe_destructor()`:
- Debug-checks VFS/device fields and delegates to `fnode_destructor()`.

`fifo_reinit_vp()`:
- Reinitializes a cached vnode for reuse and restores VFIFO type plus `VNOMAP | VNOSWAP`.

## Initialization
`fifoinit()`:
- Installs empty VFS ops and vnode ops.
- Allocates unique pseudo-device number.
- Creates global FIFOFS VFS via `fs_vfsp_global()`.
- Initializes locks and caches.
- Applies debug high-water tuning to STREAMS module info.

Module `_init()` installs the filesystem module; `_info()` returns module info.

## Shadow FIFO Vnodes
`fifovp(vnode_t *vp, cred_t *crp)`:
- Allocates a speculative fnode.
- Resolves `VOP_REALVP()` so layered aliases share the same communication endpoint.
- Initializes counts, flags, timestamps from real vnode attributes.
- Holds real vnode before acquiring `ftable_lock`.
- If an existing shadow is found, drops the speculative allocation and returns the held existing shadow vnode.
- Otherwise reinitializes the new FIFO vnode, holds underlying VFS, copies VFS/rdev/root flag, inserts into hash table, and returns it.

`fifoinsert()`, `fifofind()`, and `fiforemove()` manage the hash table. `fifofind()` holds the found FIFO vnode before returning it.

## Pipe Creation and IDs
`makepipe()`:
- Allocates a two-fnode pipe object.
- Sets both ends reader/writer counts to one.
- Marks flags `ISPIPE` plus optional `FIFOFAST`.
- Initializes timestamps.
- Reinitializes both vnodes and restores global FIFOFS VFS/device.

`fifogetid()` returns a unique anonymous pipe inode number under `fino_lock`.

## STREAMS Open Coordination
`fifo_stropen()`:
- Serializes open using `FIFOOPEN` and the shared `flk_ocsync` open/close sync flag.
- Waits if another open is in progress.
- Rejects opens on a pipe end that is closing under namefs.
- Calls `stropen()` with the FIFO lock dropped to avoid module side effects under lock.
- On first open with `dotwist`, uses `strmate()` to connect stream queues.
- Increments `fn_open`, sets `FIFOISOPEN`, clears stale `FIFOCLOSE` when writers return, and wakes waiters.
- If `FIFOCONNLD` is set, delegates special reopen/new-pipe logic to `fifo_connld()` while preserving close synchronization with a fake open.

`fifo_cleanup()`:
- Used when open is interrupted.
- Cleans locks/shares for current process and decrements reader/writer counts.

## Connld Handling
`fifo_connld()`:
- Creates a new pipe with `makepipe()`.
- Allocates a file structure for one endpoint.
- Opens both stream heads and mates them.
- Marks the returned endpoint `FIFOOPEN`.
- Marks original destination as `FIFOSEND` and verifies it is still open.
- Tags sender credentials/pid on the passed pipe descriptor.
- Sends the file pointer over the old stream using `do_sendfp()`.
- Waits until the receiver consumes the fd or a close/signal occurs.
- On success, replaces caller’s vnode with the new endpoint and closes the temporary file structure.
- On failure, closes/free/releases all temporary pipe/file state.

## Fast FIFO Mode
`fifo_fastflush()`:
- Frees queued fast-mode message data, resets byte count, and wakes writers.

`fifo_fastoff()`:
- Waits while this FIFO or paired pipe endpoint has `FIFOSTAYFAST`.
- If still fast, calls `fifo_fastturnoff()` on this endpoint and pipe peer if needed.

`fifo_fastturnoff()`:
- Moves any fast-mode queued message into the STREAMS read queue with `put()`.
- Reissues poll wakeups so STREAMS sees pending read/write readiness.
- Clears `FIFOFAST`, `FIFOWANTW`, and `FIFOWANTR`.
- Wakes waiters.

`fifo_vfastoff()` is a vnode wrapper around `fifo_fastoff()`.

## Wakeup Helpers
`fifo_wakewriter()`:
- Wakes writers sleeping below high-water mark.
- Sends poll and signal notifications for write readiness.
- Clears writer wait/high-water/poll flags.

`fifo_wakereader()`:
- Wakes readers waiting for data.
- Sends poll and signal notifications for input/read-normal readiness.
- Clears reader wait/poll flags.

## Integration Points
- Vnode/VFS ops from FIFOFS vnode implementation (`fifo_vnodeops_template` external).
- STREAMS: `stropen()`, `strmate()`, `strpollwakeup()`, `str_sendsig()`, `do_sendfp()`, queue `put()`.
- VFS/vnode lifecycle: `vn_alloc()`, `vn_reinit()`, `vn_exists()`, `vn_invalid()`, `vn_free()`, `VN_HOLD()`, `VN_RELE()`, `VFS_HOLD()`.
- Credentials and process IDs for connld descriptor passing.
- Namefs/layering via `VOP_REALVP()`.

## Risks and Subtle Areas
- FIFO open/close synchronization depends on `FIFOOPEN`, `flk_ocsync`, and wait CVs; incorrect ordering can race with `stropen()` or close hangups.
- `fifo_connld()` has many staged resources: two vnodes, a file pointer, stream opens, `FIFOSEND`, credentials, and vnode replacement.
- Fast-mode transition must preserve queued data ordering while moving messages into STREAMS.
- Shadow FIFO hash table relies on real vnode identity; layered filesystems require `VOP_REALVP()` for correctness.
- Cached vnode reuse requires `fifo_reinit_vp()` to restore expected vnode type/flags after prior lifecycle.

## Testing/Validation Signals
- Named FIFO open races and interrupted opens.
- Anonymous pipe creation and bidirectional stream mating.
- FIFO vnode shadow reuse through lofs/namefs aliases.
- `connld` open with receiver success, receiver close, signal interruption, and send failure.
- Fast FIFO read/write path followed by `putmsg/getmsg` transition to STREAMS mode.
- Poll/SIGPOLL behavior for reader and writer wakeups.
