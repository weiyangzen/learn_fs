# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract.h

`contract.h` defines the public base contract ABI. It introduces event ids, maximum parameter size, common event/detail/flag constants, common parameter ids, status field names, contract states, and contract type ids.

Public structures include `ct_event_t`, `ct_status_t`, and `ct_param_t`, carrying event buffers, status buffers, state, type, holder, zone, event counts, detail level, critical/informative masks, cookie, and parameter payload references.
