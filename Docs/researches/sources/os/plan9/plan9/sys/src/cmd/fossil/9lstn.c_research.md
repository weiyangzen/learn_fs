# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9lstn.c

Implements Fossil's console `listen` command and network listener lifecycle.

Key behavior:
- Tracks active listeners by address in a global doubly-linked list.
- `lstnAlloc()` announces an address, records listener state, and starts a `lstnListen` thread.
- `lstnListen()` accepts incoming connections and passes accepted fds to `conAlloc()`.
- `cmdLstn()` lists listeners, adds a listener, or disables one with `-d`.
- Supports listener flags `-I` for IP checking and `-N` to allow unauthenticated none attaches.

Important implementation details:
- Closing a listener's announce fd causes the listener loop to fail and free the listener.
- The listener thread name is set to `listen`.

Risks and invariants:
- Duplicate address listen attempts are rejected.
- Accept failures are logged but do not immediately stop the listener loop.
