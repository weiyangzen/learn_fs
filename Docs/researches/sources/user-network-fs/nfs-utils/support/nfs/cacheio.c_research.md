# sources/user-network-fs/nfs-utils/support/nfs/cacheio.c

Purpose: qword encoding/decoding helpers for text-based kernel cache upcall channels.

Important APIs: `qword_add()`, `qword_addhex()`, `qword_addint()`, `qword_adduint()`, and `qword_addeol()` append encoded fields to a caller-managed buffer. `qword_get()`, `qword_get_int()`, and `qword_get_uint()` parse encoded fields from a line.

Control flow: text fields encode space, tab, newline, and backslash as octal escapes and append a separating space. Hex fields begin with `\x` and emit two lowercase hex digits per byte. Decoding skips leading spaces, detects hex form, otherwise recognizes `\nnn` octal escapes, stops at space/newline/NUL, updates the input pointer, and NUL-terminates the destination.

State and persistence: no global state. It serializes/deserializes records written elsewhere to kernel cache pseudo-files.

Dependencies and integration: used by NFS cache-channel code. Depends on libc formatting/ctype and `nfslib.h`.

Risks: buffer overflow is avoided by setting remaining length negative, but callers must check the length after building. `qword_addint()` and `qword_adduint()` do not set negative length on truncation; they clamp the returned length and continue. `qword_get()` writes a NUL terminator even after hex decode, so destination buffers must reserve space if the result is treated as a string.

Test signals: round-trip spaces/tabs/newlines/backslashes, hex binary payloads including NUL bytes, truncation paths, malformed octal/hex escapes, empty fields, and integer parse failures.
