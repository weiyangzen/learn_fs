# File Research: sources/local-fs/xfsdump/librmt/rmtisatty.c

Implements `rmtisatty(fd)`.

Behavior:
- Remote descriptors always return 0.
- Local descriptors call `isatty(3)`.

Role:
- Simple compatibility wrapper for code paths that use `isatty`.
