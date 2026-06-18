# File Research: sources/os/bsd/netbsd-src/sys/fs/unicode.h

Read completely: 161 lines.

Defines two static UTF-8 helper routines intended to be included directly by filesystem code. `wget_utf8()` consumes one UTF-8 encoded character from a byte string and returns a 16-bit code unit, advancing the caller’s pointer and remaining byte count. It handles one-, two-, and three-byte UTF-8 forms, and falls back to treating invalid high bytes as ISO-8859-1-style single-byte characters. `wput_utf8()` writes one 16-bit code unit as one, two, or three UTF-8 bytes if the caller’s buffer has enough room.

The code derives from old libc locale conversion logic and is used by filesystem name translation paths such as ISO/Joliet handling.

Risks and notes: the helpers only represent `u_int16_t` values, so they do not encode or decode four-byte UTF-8 or surrogate pairs. Invalid UTF-8 fallback is permissive rather than strict. The header contains static function definitions, not just declarations, and depends on the including file to provide basic types and `KASSERT()`.
