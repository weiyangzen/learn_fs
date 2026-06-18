# File Research: sources/os/plan9/9front/sys/src/9/kw/ether1116.c

Kirkwood Marvell gigabit Ethernet driver for 88e1116/88e1121-class PHY setups used by SheevaPlug, OpenRD, and GuruPlug boards. It defines the MAC register map, RX/TX DMA descriptor formats, interrupt causes, MIB counters, PHY pages, and controller state.

The driver uses uncached, aligned RX and TX descriptor rings, a private receive block pool, explicit L1/L2 cache maintenance around DMA buffers, and a receive kproc (`rcvproc`) woken by interrupts to avoid doing all packet input at interrupt level. TX queuing is ring based, with `txreplenish`, `transmit`, and queue restart logic through `txkick`; RX uses `rxreplenish`, `receive`, and `rxkick`.

MII/PHY support is substantial. `miird`/`miiwr` drive the Marvell SMI register, `mymii` handles a board-specific dual-port PHY hack, and `kirkwoodmii` performs reset/autonegotiation/status handling. `miiphyinit` switches PHY pages to configure LEDs, RGMII power, timing delay, MDIX, and power/energy-detect behavior.

Initialization resets/quiesces the controller, programs DRAM access windows, assigns MAC/filter tables, configures SDMA burst/coalescing, enables selected interrupts, starts the RX queue, and installs the Plan 9 `Ether` entry points. Statistics are accumulated from clear-on-read MIB counters and exposed through `ifstat`.

Notable risks: several comments document hardware errata and "magic" delays/register values; jumbo mode is deliberately disabled because the input queue cannot handle it; MAC fallback for second controllers mutates controller 0's address; interrupt handling has special cases for GuruPlug RX errors and spurious TX-buffer interrupts.
