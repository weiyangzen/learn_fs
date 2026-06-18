# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether82543gc.c

## Role

Plan 9 driver for Intel RS-82543GC Gigabit Ethernet, specifically older Intel PRO/1000 server adapters. It registers as `82543GC`.

## Main Interfaces

- `ether82543gclink()` registers `gc82543pnp`.
- Provides Ethernet callbacks for attach, transmit, interrupt, ifstat, shutdown, control, promiscuous, and multicast.
- `gc82543ctl()` supports `auto on/off` and `clear stats`.

## Data Structures

- `Rdesc` and `Tdesc`: Intel legacy receive/transmit descriptors.
- `Ctlr`: MMIO register mapping, EEPROM image, descriptor rings, private RX block-pool selector, statistics, flow-control config, and multicast table shadow.
- Global free lists split short and jumbo receive buffers, though normal operation uses short buffers.

## Important Behavior

- Maps BAR0 with `vmap` and reads registers through volatile memory access.
- Reads AT93C46-style EEPROM by bit-banging `Eecd`; validates checksum `0xBABA`.
- Resets device, reloads EEPROM defaults, configures flow control and TBI autonegotiation.
- Initializes receive address registers, clears 4096-bit multicast table, and sets up RX/TX descriptor rings.
- Uses a watchdog kproc to periodically check link and replenish RX descriptors.
- RX uses a private block pool and hands completed good packets to `etheriq`.
- TX sends only when link is up and not paused; completed descriptors free their blocks.
- Multicast hashes directly from address bytes into the Intel MTA.

## Dependencies And Assumptions

- Assumes little-endian descriptor/register layout, as noted by the file header.
- No generic `ethermii.h` integration; this driver is mostly TBI/autoneg-oriented.
- Device selection accepts only Intel 82543GC fiber ID while explicitly skipping older or copper variants.

## Notable Risks

- Several comments mark tuning and GMII/MII support as incomplete.
- `gc82543recv()` drops non-EOP or errored packets without detailed error accounting.
- The RX free-block pool is global, so multiple devices share allocator state.
- Busy-wait loops during detach/reset have no scheduling backoff.
