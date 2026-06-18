# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.h

Read completely: 123 lines.

Public header for rumpclient. It declares initialization, syscall proxying, prefork/fork/exec/daemon helpers, connection retry configuration, close-notification variants, and the opaque `struct rumpclient_fork`.

It defines retry constants for infinite, once, and die-on-disconnect behavior. The inline `rumpclient__dofork()` wraps `fork` or `vfork`: it obtains prefork state, runs the host fork function, initializes the child connection, cancels on failure, and restores parent state for vfork-style execution.
