# File Research: sources/os/plan9/plan9/sys/src/9/port/mkdevc

Purpose: rc/awk generator for kernel device configuration C source.

Key logic:
- Parses config sections `dev`, `ip`, `link`, `misc`, and `port`.
- Emits includes, external `Dev` declarations, `devtab[]`, link initializers, architecture table, storage interface tables, UART physical driver table, VGA tables, IP protocol init table, custom port lines, `conffile`, and `kerndate`.
- Tracks special devices (`ad`, `sd`, `uart`, `vga`) to emit matching support arrays.
- On 386/alpha/amd64, emits i8237 DMA allocator state when any device asks for `dma`.

Dependencies and integration:
- Uses `rc`, `awk`, config files, `$objtype`, `pwd`, and generated kernel build C.

Risks and notes:
- Section parsing is indentation-sensitive.
- Device names are transformed into symbol names by convention, e.g. `foo` -> `foodevtab`.
