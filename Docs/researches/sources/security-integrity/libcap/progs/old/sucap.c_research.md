# sources/security-integrity/libcap/progs/old/sucap.c

Purpose: legacy wrapper that changes UID/GID while trying to preserve privileges for a subsequent exec.

Important APIs/functions: `wait_on_fd()` synchronizes over a pipe. `main()` rejects setuid-root use, reads current caps with `capgetp()`, forks, has the parent drop groups and switch gid/uid, then has the child restore the parent's capabilities with `capsetp(parent_pid, old_caps)` before the parent execs the target.

Control flow: parent and child coordinate through pipe close/read and `wait()`. The child performs cross-process capability mutation after the parent changes identity.

State and dependencies: mutates uid/gid/groups and capabilities across related processes. Depends on old libcap APIs, fork, pipes, passwd/group lookup, and exec.

Risks and test signals: intentionally historical and risky; asynchronous privilege restoration is fragile and not a modern safe pattern. The file is useful for understanding pre-file-capability workarounds.
