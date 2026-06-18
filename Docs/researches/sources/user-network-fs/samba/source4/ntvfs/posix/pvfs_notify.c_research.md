# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_notify.c

Purpose: implements change notify for open PVFS directory handles. It buffers notify events, manages pending requests, handles overflow, and maps SMB2 notify through the generic NTVFS mapper.

Important APIs and types: `struct pvfs_notify_buffer` is attached to `struct pvfs_file` for directory handles and stores changes, pending requests, max buffer size, current encoded size, and overflow state. Main functions are `pvfs_notify`, `pvfs_notify_setup`, `pvfs_notify_callback`, `pvfs_notify_send`, `pvfs_notify_end`, and the destructor `pvfs_notify_destructor`.

Control flow: `pvfs_notify` maps non-NTTRANS levels, resolves the directory handle, requires async-capable requests, rejects non-directory fds, creates a notify buffer if needed, queues the request, and either waits for future events or sends buffered changes asynchronously. `pvfs_notify_setup` registers with `notify_add` using recursive filter settings. The callback appends events, converts `/` to `\\`, estimates encoded length, and sends immediately except for old-name rename halves. `pvfs_notify_send` handles overflow by returning no changes and draining waiters, steals changes into the request, sets status, and either sends immediately or schedules next-event-loop send to avoid freeing active requests.

State and persistence: notify buffers are transient per open directory handle. Events are stored in memory until delivered or overflowed. The destructor unregisters from notify context and wakes pending requests.

Dependencies and integration points: depends on Samba notify context, PVFS wait/cancel messaging, tevent timers, dlink lists, and NTVFS async state. Directory mutation code such as mkdir/rmdir triggers events consumed here.

Risks: notify requires async permission; buffer overflow deliberately returns an empty change list; recursive/filter settings are not updated after initial setup except buffer size; old-name rename events are held until paired. Test signals include invalid handle, non-directory rejection, async-required behavior, event delivery, overflow drain, cancellation status, close cleanup, SMB2 mapping, recursive filter behavior, and rename old/new sequencing.
