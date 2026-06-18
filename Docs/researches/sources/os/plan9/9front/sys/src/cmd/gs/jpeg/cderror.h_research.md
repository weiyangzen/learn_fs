# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cderror.h

Application-specific error/message catalog for IJG sample programs `cjpeg`, `djpeg`, and related helpers.

Key points:
- Uses the IJG `JMESSAGE(code,string)` pattern: first inclusion without `JMESSAGE` creates an enum; later inclusion with a caller-supplied macro creates a message table.
- Defines addon message codes starting at `JMSG_FIRSTADDONCODE=1000` and ending at `JMSG_LASTADDONCODE`.
- Feature-gated messages cover BMP, GIF, PPM/PGM, Utah RLE, and Targa support.
- Common messages cover invalid color-map files, too many output colors, `ungetc` failure, unknown input format, and unsupported output format.
- If `TARGA_SUPPORTED` is not compiled, the Targa-specific diagnostic becomes a "support not compiled" message.

Dependencies and interactions:
- Included by `cdjpeg.h` after `jerror.h`, making app-specific messages available beside core JPEG library errors.
- `cjpeg.c` and `djpeg.c` include it with `JMESSAGE` defined to create `cdjpeg_message_table`, then attach that table to the IJG error manager.
- Format modules such as BMP/GIF/PPM/RLE/Targa readers and writers use these message codes.

Risk notes:
- The active enum/table contents depend on compile-time feature macros, so all compilation units that share message codes must use consistent feature definitions.
- It is not a standalone include guard in the usual sense; its multi-include behavior depends on `JMESSAGE` and `JMAKE_ENUM_LIST`.
