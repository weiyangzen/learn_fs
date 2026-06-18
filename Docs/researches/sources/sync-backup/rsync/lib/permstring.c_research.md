# sources/sync-backup/rsync/lib/permstring.c

Purpose: converts a Unix `mode_t` into an `ls -l` style permission/type string.

Important APIs/types/functions: public `permstring(char *perms, mode_t mode)` and static permission map `"rwxrwxrwx"`.

Control flow: initializes the output buffer to `"----------"`, sets rwx bits by scanning the low nine permission bits, overlays setuid/setgid/sticky characters with uppercase variants when execute is absent, and sets the leading type character for directory, symlink, block, char, socket, FIFO, or regular/unknown file.

State and persistence behavior: no internal state. Caller owns an output buffer of at least `PERMSTRING_SIZE` bytes, including the trailing null.

Dependencies/integration: includes `rsync.h` for mode macros and `strlcpy`. Used by logging/generator/tls output paths that need human-readable modes.

Risks/test signals: correctness depends on platform `S_IS*` macros, and unsupported file types remain `-`. Tests should cover all type bits, all special permission combinations, no permissions, full permissions, and buffer-size contract with `PERMSTRING_SIZE`.
