# File Research: sources/os/plan9/9front/sys/src/9/mt7688/bootargs.c

MT7688 boot-argument and `plan9.ini` parser. It stores up to 64 key/value pairs copied from `CONFADDR`, provides `getconf`, exports values into `#e`/`#ec` through `setconfenv`, and can serialize current kernel environment back to the boot-args buffer with `writeconf`.

`plan9iniinit` parses ASCII lines in place, skipping blank/comment/malformed lines and splitting on `=`.

Notable risks: `writeconf` is static and not used in this file; parsing mutates the boot buffer; fixed `MAXCONFLINE` truncates stored values through `strecpy`.
