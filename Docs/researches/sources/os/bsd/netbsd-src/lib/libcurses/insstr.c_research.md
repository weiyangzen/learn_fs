# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insstr.c

Implements narrow string insertion: `insstr`, `insnstr`, movement variants, `winsstr`, and `winsnstr`.

`winsnstr` computes the bounded input length, shifts line cells right when the inserted text fits before EOL, writes each byte as a single-column `__CHARTEXT` cell with current window attributes, clears background/continuation flags, marks the whole affected line dirty, touches it, and syncs. It does not implement multibyte decoding despite comments referring to multi-byte strings.
