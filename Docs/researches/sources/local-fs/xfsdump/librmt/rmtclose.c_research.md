# File Research: sources/local-fs/xfsdump/librmt/rmtclose.c

Implements `rmtclose(fildes)`.

Behavior:
- Local descriptors call `close(2)`.
- Remote descriptors clear remembered host type, send `C\n`, read status, then abort/close pipes.
- Returns remote status or `-1` if command send fails.

Role:
- Provides close-like semantics for local and remote tape descriptors.
