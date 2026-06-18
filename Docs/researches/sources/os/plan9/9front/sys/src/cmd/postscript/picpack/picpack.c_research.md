# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.c

`picpack.c` is a troff preprocessor that packs external picture files inline. It scans input for configured macro keys, defaulting to `.BP` and `.PI`, extracts the second argument as a picture path, and emits each unique picture in troff transparent mode with an `x X InlinePicture filename bytes` control line.

It reads each input twice: first to inline picture payloads, second to copy original troff input unchanged. Stdin is copied to an unlinked temp file to make the two-pass process possible. A separate temp file records picture names already packed, avoiding duplicates across input files.
