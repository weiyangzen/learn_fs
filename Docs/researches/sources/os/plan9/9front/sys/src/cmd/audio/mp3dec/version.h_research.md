# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.h

This header defines libmad's static version constants and declares exported metadata strings.

Key definitions:
- Version components: major `0`, minor `15`, patch `1`, extra `" (beta)"`.
- `MAD_VERSION`: stringized combined version.
- `MAD_PUBLISHYEAR`: `"2000-2004"`.
- `MAD_AUTHOR`: `"Underbit Technologies, Inc."`.
- `MAD_EMAIL`: `"info@underbit.com"`.

Exports:
- `mad_version`
- `mad_copyright`
- `mad_author`
- `mad_build`

Integration:
- Implemented by `version.c`.
- Included by code that reports decoder version/build information.

Risks:
- Version metadata is compile-time static.
- No logic, allocation, or I/O is present.
