# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_tlabel.h

This private header defines transaction-label allocation and tracking for the `hci1394` adapter.

Main types:
- `hci1394_tlabel_info_t`: destination node/bus and allocated tlabel.
- `hci1394_tlabel_t`: allocator state including max node touched, broadcast-sent optimization, free and bad bitmasks per node, last-used tlabel per node, bad-label timestamps, reclaim time, per node/tlabel lookup pointers, driver info, and mutex.

Constants:
- `TLABEL_RANGE` is `64`, the maximum 6-bit IEEE 1394 transaction label range.
- `TLABEL_MASK` extracts the 6-bit label.

APIs:
- Init/fini.
- Allocate/free.
- Register and lookup an opaque command pointer by destination/tlabel.
- Mark a tlabel bad after a pended request times out.
- Reset allocator state after bus reset.
- Update bad-label reclaim time.

Research notes:
- Bad tlabels are reclaimed only after more than twice split timeout has elapsed, reducing collision with delayed responses.
- Broadcast and max-node tracking are reset-time optimizations.
