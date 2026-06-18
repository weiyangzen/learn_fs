# File Research: sources/os/plan9/9front/sys/src/9/pc/ether589.c

## Purpose
3Com 3C589/3C562/589E PCMCIA Ethernet setup wrapper using the shared EtherLink III reset path.

## Exposed Interface
- Link function: `ether589link()`
- Registers:
  - `addethercard("3C589", reset)`
  - `addethercard("3C562", reset)`
  - `addethercard("589E", reset)`

## Implementation Notes
- Defines command/status registers and selected windowed 3Com registers.
- Uses `pcmspecial()` to locate a supported PCMCIA card.
- Defaults IRQ to 10 and I/O port to `0x240` if unspecified.
- For 3C562, reads the Ethernet address from CIS tuple `0x88` if the user did not override it, swapping byte pairs.
- Parses `media=10base2` or `media=10baseT`.
- `configASIC()` selects window 0, enables config, forces IRQ resource config, programs transceiver selection, resets TX/RX, then calls external `etherelnk3reset()`.
- Reset tries 10BaseT first when allowed, checks link beat, and falls back to 10Base2 when allowed.

## Filesystem Relevance
Network driver setup code only. Relevant as a compact example of Plan 9’s Ethernet-card registration and PCMCIA-specific hardware configuration.

## Risks / Quirks
- Comment notes 10Base2 path needs checking.
- 3C589/3C562 IRQ is effectively forced through resource config.
- Fallback media detection is simple and link-beat dependent.
