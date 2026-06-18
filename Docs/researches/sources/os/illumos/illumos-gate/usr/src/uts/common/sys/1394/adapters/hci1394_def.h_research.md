# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_def.h

This is the foundational include for the `hci1394` HAL adapter headers. It intentionally contains only definitions needed by other `hci1394` headers, plus the forward typedef `hci1394_state_t` for `struct hci1394_state_s`.

Key declarations:
- `HCI1394_MAX_ISOCH_CONTEXTS` is fixed at `32`, matching the OpenHCI maximum number of isochronous contexts.
- `typedef struct hci1394_state_s hci1394_state_t;` lets lower-level header APIs mention the soft-state type without including the full state header.

Dependencies are deliberately minimal. This header should be included before other `hci1394` adapter headers and is not meant to grow structures, prototypes, or broad macro sets.
