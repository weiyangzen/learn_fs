# File Research: sources/os/plan9/plan9/sys/src/9/kw/sdio.c

## Role

Kirkwood SDIO/MMC host driver implementing the Plan 9 `SDio` interface. It sends SD commands, manages responses, sets up DMA, handles read/write data transfers, and services SDIO interrupts.

This is directly storage-relevant: it is the SD/MMC block-device host controller backend.

## Main Interfaces

- `sdioinit`
- `sdioinquiry`
- `sdioenable`
- `sdiocmd`
- `sdioiosetup`
- `sdioread`
- `sdiowrite`
- `sdioio`
- `sdiointerrupt`

## Data Structures

- `Ctlr`: controller state including initialization, command buffer, interrupt status, wait rendezvous, and DMA bookkeeping.
- Register constants cover SDIO system address, block size/count, command, transfer mode, response registers, status, interrupt enables, clock, host control, and software reset.

## Important Behavior

- Uses `soc.sdio` as the controller register base.
- `WR` writes a register and reads it back for ordering.
- Sets SDIO clock divisors with `clkdiv`.
- Waits for command completion and transfer completion through interrupt status polling/wakeup.
- Handles 48-bit and 136-bit response formats.
- Sets up DMA by writing the physical address of the buffer.
- Read/write paths consume controller data availability and DMA done status.
- On errors, reports command/data timeout, CRC, index, end-bit, and DMA errors.

## Dependencies And Assumptions

- Implements an `SDio` backend consumed by the Plan 9 SD layer.
- Depends on `AddrSdio`/IRQ constants in `io.h`.
- Uses cache coherence helpers around DMA-relevant memory.

## Notable Risks

- DMA buffers must be physically addressable and coherent.
- Timeout constants and interrupt status handling are hardware-specific.
- Multi-block and error-recovery behavior is tightly coupled to controller status bits.
