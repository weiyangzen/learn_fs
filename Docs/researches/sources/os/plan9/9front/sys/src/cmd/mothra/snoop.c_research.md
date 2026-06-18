# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/snoop.c

MIME/type detection helper for Mothra.

Behavior:
- `filetype` reads an initial block from a file descriptor, runs `/bin/file -m` in a helper process, captures its MIME-style output, and arranges for the original descriptor stream to remain readable by forwarding the buffered prefix plus the remaining data.
- `mimetotype` maps content types to Mothra’s internal type enum, including plain text, HTML, JPEG/GIF/PNG/BMP/ICO, document/page-renderable types, generic images, generic text, and RFC822 messages.
- `snooptype` combines both steps: invoke file sniffing and convert the result to an internal type.

Important interactions:
- Used by `mothra.c` when server-provided content type is missing or not understood.
- Depends on Plan 9 process/file descriptor operations and `/bin/file`.

Notable quirks:
- The MIME map is prefix-based and intentionally small.
- Unknown types return `-1`, causing caller policy to decide whether to save, plumb, or report.
