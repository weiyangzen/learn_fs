# sources/test-tools/liburing/examples/helpers.c

## sources/test-tools/liburing/examples/helpers.c

Purpose: Shared helper implementation for example programs.

Important APIs/functions: fallback `memfd_create` via `syscall(SYS_memfd_create)` when `CONFIG_HAVE_MEMFD_CREATE` is absent; `setup_listening_socket(int port, int ipv6)`; `t_aligned_alloc`; `t_error`.

Control flow: `setup_listening_socket` selects IPv4/IPv6 domain, creates stream socket, enables `SO_REUSEADDR`, binds to wildcard address, listens with backlog 1024, and returns fd. Allocation wrapper delegates to `posix_memalign`. Error helper prints formatted message plus optional errno string then exits.

State and persistence: creates listening sockets and heap allocations for callers. No global state.

Dependencies/integration: used by echo server, proxy, registered wait, zcrx, and other examples needing socket setup, aligned allocation, or test-style fatal errors.

Risks: on setsockopt/bind/listen failures, the socket fd is not closed before returning `-1`, causing minor leaks in failing examples. `t_error` exits directly, unsuitable for library contexts. Fallback `memfd_create` declaration may conflict if config detection is wrong.

Test signals: example builds and runtime paths that use socket setup/aligned allocation.
