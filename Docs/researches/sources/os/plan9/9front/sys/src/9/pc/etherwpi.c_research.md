# File Research: sources/os/plan9/9front/sys/src/9/pc/etherwpi.c

Implements the Intel PRO/Wireless 3945ABG `wpi` driver, integrating PCI MMIO hardware setup, firmware loading, DMA rings, 802.11 command handling, and the generic 9front Wi-Fi layer.

Key elements:
- Registers as `wpi` and matches Intel PCI IDs `0x8086:0x4222` and `0x8086:0x4227`.
- Defines register maps for device control, flow handler RX/TX DMA, peripheral registers, firmware boot memory, and NIC internal scheduling/power-management state.
- `Ctlr` tracks PCI/MMIO state, firmware image, EEPROM calibration data, RX/TX queues, shared DMA status page, Wi-Fi state, channel/BSSID/AID, node IDs, power state, and recovery flags.
- `wpiinit()` powers the NIC, validates EEPROM signature, reads MAC address, regulatory domain, channel max power, and calibration power groups, then powers the NIC off.
- `readfirmware()` loads firmware from `/boot/wpi-3945abg` as Eve or `/lib/firmware/wpi-3945abg`, parses it into init/main/boot text and data sections using `crackfw()`.
- `reset()` initializes RX/TX rings, powers on, sets adapter configuration from EEPROM/revision data, programs RX DMA, TX scheduler, TX DMA queues, interrupt masks, and firmware wake flags.
- `boot()` DMA-loads init firmware sections, copies boot microcode into NIC SRAM, waits for alive interrupts, loads main firmware sections, and runs `postboot()`.
- `qcmd()` is the central command/TX queue builder. It waits for queue space, fills command and transmit descriptors, attaches an optional packet block, updates host write pointer, and handles broken-controller state.
- `cmd()` sends synchronous commands through queue 4 and waits for completion using `flushq()`.
- `rxon()` configures station receive mode, BSSID/channel/AID, filters, LED state, TX power tables, broadcast node, and associated BSS node.
- `transmit()` is the Wi-Fi TX callback. It updates RXON state if BSS/channel changed, selects rate and node ID, sets ACK/RTS flags, builds command 28, and queues the packet.
- `receive()` processes firmware notifications and RX descriptors, reclaims TX blocks, handles RX done packets, validates frame status, replants RX buffers, and passes frames to `wifiiq()`.
- `wpiinterrupt()` masks interrupts, acknowledges device and flow-handler interrupts, runs receive processing, marks fatal firmware errors, wakes waiters, and restores interrupt mask.
- `wpirecover()` periodically attempts recovery when `ctlr->broken` is set and RF kill permits operation.
- `wpiattach()` attaches Wi-Fi state, loads firmware, resets and boots firmware, applies options, and starts recovery.
- `wpictl()` supports a `reset` control command by marking the controller broken; otherwise it delegates to `wifictl()`.

Filesystem relevance: indirect only through firmware file reads. This is primarily a firmware-driven wireless network driver and a useful example of Plan 9 device code that loads firmware through kernel name lookup and device read paths.
