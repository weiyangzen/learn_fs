# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2pdf13

PostScript-to-PDF wrapper targeting PDF 1.3 compatibility.

Behavior:
- Executes `ps2pdfwr -dCompatibilityLevel=1.3 "$@"`.

Filesystem relevance:
- Process delegation wrapper only.
