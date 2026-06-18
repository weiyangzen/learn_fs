# sources/test-tools/syzkaller/vm/vmimpl/util.go

Purpose: shared utility functions for VM implementations, especially interruptible sleep, SSH/SCP option construction, waiting for SSH boot readiness, random port allocation, and shell double-quote escaping.

Important APIs/types/functions: `SleepInterruptible`, `SSHOptions`, `WaitForSSH`, `ErrCantSSH`, `SSHArgs`, `SSHArgsForward`, `SCPOptions`, `SCP`, `RandomPort`, `UnusedTCPPort`, and `EscapeDoubleQuotes`.

Control flow: `WaitForSSH` sleeps briefly, then every five seconds runs `ssh user@addr pwd` or Windows `dir` until success, stop-channel error, global shutdown, or timeout. SSH/SCP argument helpers add isolated config, known-host suppression, identity options, timeouts, optional key, verbose mode, and reverse forwarding. `SCP` runs legacy-protocol `scp` with timeout and wraps failures. `UnusedTCPPort` samples random high ports until `net.Listen` succeeds or an unexpected listen error is fatal. `EscapeDoubleQuotes` walks bytes and re-escapes double quotes and quote-directed backslash sequences.

State and persistence: no durable state. Port allocation is inherently transient; SSH/SCP operate on guest/host files as requested by callers.

Dependencies and integration: used by most VM backends for boot readiness, file copy, command forwarding, and safe shell construction.

Risks: random free port can race later bind; `WaitForSSH` consumes only one stop error and can wait full intervals; `scp -O` assumes legacy protocol availability; escaping is byte-oriented and bash-specific.

Test signals: exercised indirectly by backend integration tests; no direct unit test is assigned here.
