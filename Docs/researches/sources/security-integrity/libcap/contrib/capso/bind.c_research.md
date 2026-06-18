<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/bind.c -->
# sources/security-integrity/libcap/contrib/capso/bind.c

## Purpose
Unprivileged demo executable that calls `capso` to bind port 80 and then listens.

## Important APIs, Types, And Functions
Uses `bind80` from `capso.h`, `listen`, `sleep`, `close`, `perror`, and stdout status messages.

## Control Flow
Calls `bind80("127.0.0.1")`, exits on failure, calls `listen`, prints the file descriptor, sleeps for 60 seconds for inspection, then closes the socket.

## State And Persistence Behavior
Creates a listening socket on TCP port 80 for up to 60 seconds. Does not persist files.

## Dependencies And Integration Points
Links against `capso.so`, which may launch itself with file capabilities to obtain the privileged socket.

## Risks And Edge Cases
Requires port 80 to be free. Sleeping server behavior is demo-only and can temporarily expose a listening socket.

## Test Signals
Signals are successful bind/listen and visible port 80 listener during the sleep window.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/bind.c -->
