# sources/security-integrity/gocryptfs/daemonize.go

Purpose: This file implements gocryptfs foreground/background daemonization behavior in Go.

Important APIs and functions: `exitOnUsr1` waits for mount-success notification. `forkChild` re-executes the current binary with `-fg`, wires notification through `-notifypid`, and returns success/failure based on signal or child exit. `redirectStdFds` redirects stdin/stdout/stderr for background operation and syslog behavior.

Control flow and state: Parent process waits for SIGUSR1 from the child mount process, then exits. The child becomes the foreground mount process. Process arguments and file descriptors are mutated.

Dependencies and integration points: Integrates with CLI flags, FUSE mount startup, syslog logging, and service managers.

Risks and test signals: Re-exec and signal timing are fragile. Risks include lost notifications, bad fd redirection, and incorrect exit code propagation. Signals are successful background mount notification and clean failure when child exits early.
