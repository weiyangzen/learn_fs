# File Research: sources/os/plan9/9front/sys/src/cmd/dict/world.c

Adapter for “Languages of the World” dictionary binary format.

Key elements:
- Entry begins with three big-endian 16-bit lengths: headword, pronunciation/part, and definition sections.
- `worldprintentry` skips the six-byte header, prints only headword length in `h` mode, or the full entry otherwise.
- `worldnextoff` computes the next entry offset from header lengths and requires being called with valid-entry address plus one.
- `putchar` decodes a custom byte encoding with normal single-byte table, Shift-JIS/JIS Japanese mode, and GB mode.
- Uses `tabjis208` and `tabgb2312` after converting double-byte pairs with `S2J`.
- Maintains state for UTF/single-byte mode, Japanese high/low byte, GB high/low byte, and suppressible extended mode.

Dependencies:
- Includes `kuten.h`.
- Uses `jis208.c` and `gb2312.c` tables.

Research notes:
- This one adapter serves many bilingual dictionaries via different data/index paths in `utils.c`.
