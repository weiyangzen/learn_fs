# sources/security-integrity/ecryptfs-utils/src/daemon/main.c

Purpose: implements `ecryptfsd`, the userspace daemon that responds to eCryptfs kernel module requests over `/dev/ecryptfs`.

Important APIs/functions: `prompt_callback()` runs an external prompt program and reads password output; `daemonize()` double-forks, redirects stdio to `/dev/null`, closes fds, and ignores initial signals; `sigterm_handler()` exits through `ecryptfsd_exit()`; `main()` parses options, validates kernel version, configures daemon mode/chroot/pidfile/signals, initializes messaging, sends `ECRYPTFS_MSG_HELO`, runs `ecryptfs_run_daemon()`, then sends quit/cleans up.

Control flow: command-line options include pidfile, foreground, chroot, prompt program, version, and help. The daemon refuses kernels lacking miscdev support when version retrieval succeeds. It disables core dumps to avoid secret leakage. A global messaging context is protected by `mctx_mux` around state changes and signal-driven exit.

State/persistence: optional pidfile is written/unlinked; environment `TERM_DEVICE` records tty; daemon may chroot; syslog records events. Messaging state persists in `mctx`.

Dependencies/integration: libc/POSIX process APIs, pthread, syslog, `config.h`, and libecryptfs messaging/key prompt APIs.

Risks: `prompt_callback()` waits for child completion before reading pipe output, so large prompt output could deadlock, though password output should be small. `daemonize()` loops `dup2(null, 0)` for fd 0..2, likely intending `dup2(null, fd)`. Signal handler performs mutex and complex cleanup, which is not async-signal-safe.

Test signals: daemon startup against `/dev/ecryptfs`, option parsing, pidfile cleanup, and kernel message round-trip tests.
