# sources/sync-backup/rsync/testsuite/bare-do-open-symlink-race_test.py

Purpose: daemon receiver security regression for bare `do_open`, `do_symlink`, and `do_mknod` paths following parent symlinks out of a module.

Important APIs/types/functions: `setup`, `positive_control`, `run_attack`, `verify_outside_unchanged`, `verify_outside_unchanged_or_absent`, daemon config for normal and fake-super modules, uid/gid helpers, `mkfifo`, and platform skip.

Control flow: skip on platforms lacking needed secure-open support. Start one daemon with `upload` and `upload_fake`. First prove normal uploads work. Then run three attacks through `module/cd -> outside`: `--inplace --backup --backup-dir=cd`, fake-super symlink push, and fake-super FIFO push. Each must not signal-crash and must not change/create outside files.

State and persistence behavior: outside sentinel content/mode and absence of created `sym`/`fifo` are the security oracles. Fake-super module changes receiver metadata encoding paths.

Dependencies and integration points: daemon receiver path confinement, fake-super, symlink/mknod/open wrappers, platform kernel support, and test daemon.

Risks and test signals: skips if FIFO unavailable. Positive control avoids vacuous passes. Any outside mutation means module escape via a low-level syscall wrapper.
