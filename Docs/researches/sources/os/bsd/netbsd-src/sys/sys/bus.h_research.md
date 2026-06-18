# File Research: sources/os/bsd/netbsd-src/sys/sys/bus.h

## Scope

Top-level bus space and bus DMA abstraction header, selecting new-style or legacy machine bus APIs.

## APIs And Data Structures

- Under `__HAVE_NEW_STYLE_BUS_H`, includes machine bus definitions and defines `bus_space_reservation_t` with accessors/init helpers.
- Defines override bit indices for bus space and bus DMA operations.
- `bus_space_overrides` and `bus_dma_overrides` contain optional function pointers for map/unmap/alloc/free/reserve/DMA map/memory operations.
- Declares bus space and DMA tag create/destroy, reserve/release, reservation map/unmap, and subregion reservation.
- Includes `sys/bus_proto.h` and `machine/bus_funcs.h`.
- Legacy path includes `machine/bus.h` and declares equality helpers.
- Provides dummy bus DMA types for ports with `__HAVE_NO_BUS_DMA`.
- Defines `BUS_ADDR_HI32` and `BUS_ADDR_LO32`.

## Dependencies

- Includes `sys/types.h`, machine bus headers, and cdefs bit helpers.

## Risks And Invariants

- Override structures explicitly require adding new members only at the end.
- New-style and legacy paths expose different implementation details but must satisfy MI drivers.
