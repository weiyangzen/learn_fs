# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact_aout.h

`imgact_aout.h` defines legacy a.out executable header handling. It includes `sys/types.h`.

The header provides macros to get/set magic, machine ID, and flags in host or network byte order; validate magic numbers; compute aligned text/data/relocation/symbol/string offsets; and compute text/data virtual addresses. It supports `OMAGIC`, `NMAGIC`, `ZMAGIC`, and `QMAGIC`.

`struct exec` models the a.out header, with `aout_register_t` optionally forced to 32-bit via `AOUT_H_FORCE32`. The file also defines historical machine IDs and dynamic/PIC flags. It is legacy executable-format ABI support.
