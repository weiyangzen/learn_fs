# sources/security-integrity/selinux/sandbox/test_sandbox.py
# sources/security-integrity/selinux/sandbox/test_sandbox.py

Purpose: integration tests for sandbox CLI behavior under enforcing SELinux.

Important APIs and control flow: `SandboxTests` runs subprocesses for simple stdin use, denied kill/ping/mail/sudo operations, failed mkdir/list-home operations, mount mode, explicit level, alternate homedir/tmpdir, and included-file copying. Main guard runs only when SELinux is enabled and enforcing.

State and persistence: creates temporary dirs for homedir/tmpdir tests and removes them; sandbox itself may create temporary dirs and labels.

Dependencies and integration points: depends on local `sandbox` script, SELinux enforcing policy, common utilities (`cat`, `grep`, `kill`, `ping`, `mkdir`, `ls`, `mail`, `sudo`, `id`), and Python executable.

Risks and test signals: tests assert broad success/failure and selected error text, but not exact SELinux contexts or cleanup. They are valuable smoke tests but environment-sensitive.
