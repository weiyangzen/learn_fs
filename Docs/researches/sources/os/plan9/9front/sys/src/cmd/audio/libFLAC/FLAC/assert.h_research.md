# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/assert.h

libFLAC assertion wrapper header.

Important contents:
- In non-`NDEBUG` builds, includes `<assert.h>` and maps `FLAC__ASSERT` to `assert`.
- In release builds, assertion macros compile away.
- `FLAC__ASSERT_DECLARATION` conditionally retains debug-only declarations.

This keeps libFLAC assertions independent of platform-specific assert conventions.
