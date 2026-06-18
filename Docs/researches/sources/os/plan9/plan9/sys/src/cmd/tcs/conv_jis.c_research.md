# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_jis.c

Japanese encoding converters for `tcs`: mixed JIS detection, ISO-2022-JP, Shift-JIS, and EUC-JP.

Input state machines:
- `alljis` handles escape shifts plus possible Shift-JIS byte pairs.
- `ms` handles Shift-JIS, using `CANS2J` and `S2J` to convert to kuten indices.
- `ujis` handles EUC-JP two-byte codes and rejects codeset 2/3.
- `jis` handles ISO-2022-JP style escape shifts and guards against mixed Latin-1/JIS byte pairs.
- `do_in` is the shared streaming wrapper.

Output functions:
- `jisjis_out` emits ISO-2022-JP escape transitions.
- `msjis_out` emits Shift-JIS using `J2S`.
- `ujis_out` emits EUC-JP.
- `tab_init` builds reverse rune-to-kuten mapping from `tabkuten208`.

Notable behavior:
- Supports Japan646 mappings for backslash to yen and tilde to macron in relevant states.
- Negative table entries represent ambiguous mappings; they are emitted as positive code points with optional diagnostics.
