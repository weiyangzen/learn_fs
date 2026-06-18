# File Research: sources/os/plan9/9front/sys/src/9/port/cis.c

PCMCIA Card Information Structure parser.

Key behavior:
- `pcmcistuple` searches attribute space first, then common memory, for a tuple/subtuple and copies tuple payload bytes.
- `pcmcisread` resets a `PCMslot`’s parsed config state and walks CIS tuples from attribute memory.
- Tuple handlers parse long-link multi-function tuples, version strings, config register bases/masks, and config table entries.
- Utility parsers decode little-endian variable-size integers, voltage/current encodings, timing encodings, I/O ranges, IRQ masks, and memory windows.
- Config entries populate `PCMconftab` fields such as index, default config, memory wait, Vpp, timing, I/O windows, 16-bit I/O capability, IRQ type/mask, and config-present state.
- Version tuples are normalized into semicolon-separated strings.

Notable dependencies:
- PCMCIA mapping functions `pcmmap` and `pcmunmap`.
- `PCMslot`, `PCMmap`, and `PCMconftab` architecture structures.

Research notes:
- The tuple scan has hard iteration limits for direct tuple lookup and stops on `0xff` end markers.
- IRQ masks are filtered with a hardcoded available-level mask.
- Memory-space tuple details are consumed to keep parsing in sync but not stored by this file.
