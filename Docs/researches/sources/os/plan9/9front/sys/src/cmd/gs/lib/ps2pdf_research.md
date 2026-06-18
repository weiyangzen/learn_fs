# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2pdf

Compatibility wrapper for PostScript-to-PDF conversion.

Behavior:
- Delegates directly to `ps2pdf14 "$@"`.
- Comment notes default PDF version is currently 1.4 but not guaranteed forever.

Filesystem relevance:
- Process delegation wrapper only.
