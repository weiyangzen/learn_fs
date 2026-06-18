<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.c -->
# sources/security-integrity/libcap/contrib/capso/capso.c

## Purpose
Shared-object capability demonstration. It exposes `bind80()` and can execute itself as a helper with file capabilities to bind privileged port 80 and pass the socket back.

## Important APIs, Types, And Functions
Key functions include `fake_exploit`, `where_am_i`, `try_bind80`, `set_fd3`, `bind80`, and `SO_MAIN`. Uses libcap `cap_get_proc`, `cap_set_flag`, `cap_set_proc`, launcher APIs, sockets, `SCM_RIGHTS`, and dynamic loader introspection.

## Control Flow
`bind80` first tries to bind directly. On failure it locates its own shared object, creates a Unix datagram socketpair, launches itself as an executable helper with fd 3 mapped to the socket, and receives the bound fd by `recvmsg`. The shared-object main raises effective `CAP_NET_BIND_SERVICE`, binds, sends the fd over fd 3, and optionally executes exploit-demo code when compiled/enabled.

## State And Persistence Behavior
Creates sockets, launches a child process, and transfers file descriptors. The build installs a persistent file capability on the `.so`; runtime capability changes are process-local.

## Dependencies And Integration Points
Depends on libcap launcher and capability APIs, `execable.h`, dynamic loader support, Unix sockets, and the makefile-set file capability.

## Risks And Edge Cases
This is security-sensitive demo code. Helper launch, fd passing, environment handling, and optional exploit simulation must not be treated as production-hardening. Port availability and filecap setup affect behavior.

## Test Signals
Signals are direct or helper bind success, receipt of a valid fd via `SCM_RIGHTS`, and usable listener from `bind.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.c -->
