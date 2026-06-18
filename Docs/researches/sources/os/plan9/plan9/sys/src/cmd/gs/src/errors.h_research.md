# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/errors.h

Backward-compatibility wrapper for Ghostscript API errors.

Key points:
- Explains that old client API error definitions moved to `ierrors.h`.
- Includes `ierrors.h` to preserve compatibility with older code including `errors.h`.

Dependencies and interactions:
- No definitions of its own beyond the include guard and compatibility include.

OS/filesystem relevance:
- None directly; it keeps error-code includes stable for client code.
