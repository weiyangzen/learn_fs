# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cderror.h

Application-specific IJG message-code header for `cjpeg`, `djpeg`, and their image format modules.

Key behavior:
- Uses the IJG `JMESSAGE(code,string)` inclusion pattern.
- On first inclusion without `JMESSAGE`, defines the `ADDON_MESSAGE_CODE` enum beginning at `JMSG_FIRSTADDONCODE=1000`.
- On repeated inclusion without `JMESSAGE`, expands to no-ops.
- When included with a caller-defined `JMESSAGE`, emits message table entries.
- Defines conditional error/trace/warning messages for BMP, GIF, PPM/PGM, RLE, and Targa support.
- Defines shared application messages for bad color map files, excessive output colors, failed `ungetc`, unknown input format, and unsupported output format.
- Ends enum generation with `JMSG_LASTADDONCODE`.

Dependencies:
- Depends on feature macros such as `BMP_SUPPORTED`, `GIF_SUPPORTED`, `PPM_SUPPORTED`, `RLE_SUPPORTED`, and `TARGA_SUPPORTED`.
- Intended to be used with IJG `jerror.c`/`jpeg_error_mgr` addon message table fields.

Research notes:
- This header is deliberately multi-include and macro-driven.
- Message availability changes at compile time with supported image formats, so numeric addon codes depend on build configuration.
