# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socketvar.h

## Role

Private sockfs kernel header defining the internal socket object, socket module registry, socket parameter table, fallback support, sendfile queues, operation vectors, and sockconfig data structures.

## Key Contents

Defines AF_UNIX transport-level address structures used to avoid pathname ambiguity. Defines `struct sonode`, the core in-kernel socket object associated with a vnode, including locks, state flags, socket identity, accept queues, options, OOB state, credentials, zone, poll state, receive queues, protocol handles/downcalls, kernel socket callbacks, direct receive support, filters, and callback hooks.

Defines state flags such as connection state, shutdown state, async/listen/OOB/filter/fallback status, socket modes, socket version constants, socket module registration structures, `sockparams`, reference-count macros, sendfile request/queue structures, and `sonodeops`.

## Interfaces

Declares sockparams and socket module registry functions, sockfs lifecycle and data conversion helpers, file-descriptor passing helpers, state transition helpers, wrapper operations such as `sobind`, `soconnect`, `sorecvmsg`, `sosendmsg`, and kernel direct receive callback functions.

## Design Notes

Locking is central: `so_lock`, single/read locks, accept queue lock, fallback rwlock, and filter state all coordinate access. The file also defines public-ish kstat export structures and `sockconfig()` command data for socket/filter administration.
