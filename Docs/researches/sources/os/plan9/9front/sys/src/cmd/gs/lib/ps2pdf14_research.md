# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2pdf14

PostScript-to-PDF wrapper targeting PDF 1.4 compatibility.

Behavior:
- Executes `ps2pdfwr -dCompatibilityLevel=1.4 "$@"`.

Filesystem relevance:
- Process delegation wrapper only.
