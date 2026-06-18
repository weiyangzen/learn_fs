# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.c

This file defines libmad version/build metadata strings.

Key exports:
- `mad_version`: `"MPEG Audio Decoder " MAD_VERSION`.
- `mad_copyright`: copyright year plus author.
- `mad_author`: author and email.
- `mad_build`: concatenated compile-time feature string.

Dependencies and integration:
- Includes `global.h` and `version.h`.
- The strings declared here are exported by `version.h`.
- Build metadata is selected by preprocessor defines such as `DEBUG`, `NDEBUG`, `EXPERIMENTAL`, fixed-point implementation flags, assembly optimization flags, and optimization-mode flags.

Notable behavior:
- `mad_build` is a compile-time string literal assembled from enabled flags.
- `OPT_DCTO` is checked but commented as never defined here, because it is local to synthesis compilation conditions.

Risks and edge cases:
- Build metadata only reflects macros visible while compiling this translation unit; flags local to other files may not appear.
- No runtime logic or filesystem behavior is present.
