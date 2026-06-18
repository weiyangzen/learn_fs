# sources/sync-backup/rsync/testsuite/chmod-symlink-race_test.py

Purpose: security regression for receiver-side chmod operations escaping through parent symlinks, delegated to the compiled helper `t_chmod_secure`.

Important APIs/types/functions: filesystem setup of `module`, `trap`, symlinks `inside_link` and `escape_link`, `subprocess.run([TOOLDIR/t_chmod_secure, mod])`, and final Python sentinel mode check.

Control flow: build in-module and outside sentinel files, symlink shapes expected by the helper, run `t_chmod_secure`, fail on helper error, then verify the outside sentinel mode remains `0600`.

State and persistence behavior: outside `trap/sentinel` mode is the security oracle; in-module paths provide positive and negative chmod targets.

Dependencies and integration points: compiled rsync test tool `t_chmod_secure`, receiver `do_chmod_at` hardening, and symlink path semantics.

Risks and test signals: relies on helper coverage for the detailed scenario enumeration. Failure means chmod escaped module confinement or helper detected another secure-chmod bug.
