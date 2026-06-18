# File Research: sources/local-fs/xfsdump/man/Makefile

Top-level manpage Makefile.

Behavior:
- Includes build definitions from parent.
- Defines `SUBDIRS = man8`.
- Default builds subdirectories.
- Install and install-dev recurse into subdirectories through pattern rules.

Role:
- Delegates manual page build/install handling to `man/man8`.
