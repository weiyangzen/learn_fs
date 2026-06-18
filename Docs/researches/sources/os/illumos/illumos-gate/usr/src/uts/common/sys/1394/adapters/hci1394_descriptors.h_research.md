# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_descriptors.h

This header defines OpenHCI 1394 DMA descriptor formats, descriptor bitfields, packet header bitfields, and helper macros used by asynchronous and isochronous transmit/receive paths.

Main data structures:
- `hci1394_desc_t`: 16-byte descriptor with `hdr`, `data_addr`, `branch`, and `status`.
- `hci1394_desc_imm_t`: immediate descriptor carrying four extra packet header quadlets.
- `hci1394_desc_hdr_t`: the four immediate packet header quadlets by themselves.
- `hci1394_basic_pkt_t`: generic receive/transmit packet view with up to five quadlets, including status/rescount for AR/IR.

Important constants and macros:
- `HCI1394_DESC_MAX_Z` limits descriptor block components to eight 16-byte units.
- Descriptor command type/key/branch/interrupt/status macros encode OpenHCI command words for AT, AR, IT, and IR.
- `HCI1394_SET_BRANCH`, `HCI1394_GET_BRANCH_ADDR`, and `HCI1394_GET_BRANCH_Z` manage branch pointer plus Z-count encoding.
- `HCI1394_INIT_IT_*` and `HCI1394_INIT_IR_*` initialize common isochronous transmit/receive descriptor sequences.
- Packet field getters/setters cover tcode, tlabel, rcode, source/destination IDs, data length, extended tcode, PHY generation, and isochronous tag/channel/sy fields.

Research notes:
- Descriptor status event values are mirrored from OpenHCI context status and include both event codes and ACK response codes.
- Some macros reference names that are expected from related headers, especially OHCI context masks. The include ordering in the full driver matters.
- A few isochronous macros appear to use inconsistent names (`DESC_TAG_MASK`, `PKT_CHAN_MASK`, `DESC_DATALEN_MASK`) while this file defines `DESC_PKT_*` variants. Treat those as compatibility or latent typo points when following call sites.
