# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.h

Header for the minimal select-based event API.

Key contents:
- Active only under `USE_MINI_EVENT && !USE_WINSOCK`.
- Renames libevent-style symbols into `minievent_*` / `minisignal_*` namespace with macros to avoid linker crosslinking of private symbols.
- Defines event bit flags:
  - `EV_TIMEOUT`
  - `EV_READ`
  - `EV_WRITE`
  - `EV_SIGNAL`
  - `EV_PERSIST`
- Includes `rbtree.h` for timeout ordering.
- Defines limits:
  - `MAX_FDS 1024`
  - `MAX_SIG 32`
- Defines `struct event_base`:
  - timeout rbtree;
  - fd-to-event array;
  - max/capacity fd tracking;
  - fd sets for reads, writes, ready, content;
  - signal event array;
  - loop-exit flag;
  - pointers to externally stored current time.
- Defines `struct event`:
  - rbtree node;
  - added flag;
  - base pointer;
  - fd/signal number;
  - event interest bits;
  - timeout value;
  - callback and callback argument.
- Declares event and signal functions plus `evtimer_add/del` and `signal_set` convenience macros.
- Declares `mini_ev_cmp` outside the conditional so the comparator symbol remains visible for whitelist/test references.

Research notes:
- This is a compatibility shim, not a full libevent replacement.
- Callers must call `event_base_set` for every event before adding it.
