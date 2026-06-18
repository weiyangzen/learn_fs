# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock.h

Defines private kernel record-locking declarations and instrumentation. It introduces `F_REMOTELOCK` and `F_PXFSLOCK`, reclock command bits (`INOFLCK`, `SETFLCK`, `SLPFLCK`, remote/PXFS/nonblocking-mandatory bits), `IGN_PID`, unsigned lock offset types, and maximum offset constants.

`pad_info_t` describes private interpretation of `struct flock.l_pad`, especially `F_HASREMOTELOCKS`. `flk_callback_t` supports before/after sleep callbacks for blocking lock requests and CPR-safe suspension. `filock_t` is retained mostly for pointer casts, while `grant_lock_t` batches locks to grant.

The file defines NLM and lock-manager status enums, kernel `locklist_t` for active/sleeping lock queries, query flags, OFD lock helpers, core lock functions (`reclock`, `chklock`, `convoff`, `cleanlocks`), lock-list query/free helpers, lock data conversion/checking, remote-lock checks, lock-manager status update, callback list operations, zone hooks, and clustering hooks for NLM/PXFS lock handling.
