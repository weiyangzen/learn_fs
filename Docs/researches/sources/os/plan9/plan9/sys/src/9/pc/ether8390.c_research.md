# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8390.c

## Role

Shared Plan 9 support code for National Semiconductor DP8390 and compatible Ethernet NIC cores, used by board-specific NE2000/SMC-style drivers.

## Main Interfaces

- Exports `dp8390reset`, `dp8390read`, `dp8390getea`, and `dp8390setea`.
- Installs generic Ethernet callbacks during `dp8390reset`: attach, transmit, interrupt, shutdown, promiscuous, multicast.
- Relies on board-specific `Dp8390` fields and low-level access helpers from `ether8390.h`.

## Data Structures

- `Hdr`: DP8390 receive-ring packet header.
- Uses `Dp8390` from `ether8390.h` for port/data width, shared-memory mode, ring page numbers, multicast shadow, and transmit state.

## Important Behavior

- Implements DP8390 remote DMA reads/writes through register setup plus data-port transfer.
- Supports both shared-memory cards and remote-DMA I/O cards.
- Handles optional dummy remote-read sequence for boards that require it before writes.
- Initializes the receive ring using page pointers `pstart`, `pstop`, `nxtpkt`, and `Bnry`.
- RX path reads ring headers, validates next-page and length, handles wraparound, copies packets into Plan 9 blocks, and advances boundary.
- TX path pads short packets, writes them to card memory, starts transmission, and tracks `txbusy`.
- Interrupt path handles receive, transmit complete/error, counter overflow, and overflow recovery using the datasheet-prescribed sequence.
- Multicast uses `ethercrc`, a 64-bit hash table, and reference counts for filter bits.

## Dependencies And Assumptions

- Depends on `ether8390.h` macros/functions: `regr`, `regw`, `rdread`, and `rdwrite`.
- Assumes board driver has set ring memory layout, transfer width, and data port correctly before `dp8390reset`.
- Maximum accepted RX packet is `sizeof(Etherpkt)`.

## Notable Risks

- Remote DMA waits use spin timeouts and may silently proceed after timeout in some paths.
- Ring corruption causes full ring reinitialization and packet loss.
- Only one transmit packet is active at a time.
- Header comments and behavior assume old DP8390 clone quirks, so board setup is critical.
