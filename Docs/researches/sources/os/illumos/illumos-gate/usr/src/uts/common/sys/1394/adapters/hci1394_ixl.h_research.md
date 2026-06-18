# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_ixl.h

This private header supports compiling and dynamically updating public IXL programs into OpenHCI isochronous DMA descriptor chains.

Main structures:
- `hci1394_xfer_ctl_dma_t`: bound address with Z bits, kernel descriptor pointer, and DMA buffer info for one descriptor block.
- `hci1394_xfer_ctl_t`: per-transfer control node with execution pointer, optional skipmode command, flags, descriptor-block count, and flexible `dma[]` array.
- `hci1394_comp_ixl_vars_t`: large temporary compiler state for converting IXL commands into descriptor blocks, tracking current command, descriptor memory, transfer state, updateable command flags, packet/buffer fragments, receive sync-wait count, and transmit skip/tag/sync state.
- `hci1394_ixl_update_vars_t`: dynamic update state, including old/new commands, current execution location window, skip/jump/buffer/header fields to patch, risk level, opcode, and status.

Constants:
- Interrupt sync return values distinguish normal, in-update, DMA stopped, DMA lost, no-advance exhaustion, and fatal internal states.
- `HCI1394_IXL_MAX_SEQ_JUMPS` caps label/jump complexity between transfers at 10.
- `UPDATEABLE_*` and `XFER_*` flags describe compilation state.

Key APIs:
- `hci1394_compile_ixl`, `hci1394_ixl_update`, `hci1394_ixl_interrupt`, `hci1394_ixl_dma_sync`, `hci1394_ixl_set_start`, status helpers, execution search, and cleanup.

Research notes:
- This is the bridge between target-visible IXL commands (`ixl1394.h`) and device-visible OpenHCI descriptors (`hci1394_descriptors.h`).
- Dynamic update correctness depends on knowing where hardware is currently executing; the location array holds current plus following transfers.
