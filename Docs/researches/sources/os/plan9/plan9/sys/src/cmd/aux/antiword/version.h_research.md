# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/version.h

This header defines Antiword release strings.

Key behavior:
- Sets purpose, author, version, platform-specific secondary version, and status strings.
- Version is `0.37  (21 Oct 2005)`.
- Debug builds identify themselves as `DEBUG version`; release builds report GPL status.

Important details:
- RISC OS author string uses a copyright symbol variant, while other platforms use ASCII `(C)`.

Filesystem relevance:
- None directly.
