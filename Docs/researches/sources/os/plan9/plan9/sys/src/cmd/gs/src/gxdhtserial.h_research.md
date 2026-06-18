# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.h

Declares halftone serialization API.

- Forward-declares `gs_memory_t`, `gx_device`, `gx_device_halftone`, and `gs_imager_state`.
- Declares `gx_ht_write`:
  - serializes a halftone to caller-provided buffer
  - reports required/used size through `psize`
- Declares `gx_ht_read_and_install`:
  - reconstructs a halftone from serialized bytes
  - installs it directly as current imager-state halftone
  - returns bytes read or negative error
- Notes that read and install are combined to avoid unnecessary allocation.

Minor issue: closing include-guard comment spells `gxdhtserail_INCLUDED`, while the actual guard is `gxdhtserial_INCLUDED`.
