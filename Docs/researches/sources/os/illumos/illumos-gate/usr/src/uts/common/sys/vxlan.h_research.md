# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vxlan.h

`vxlan.h` provides the common VXLAN wire-header definitions. It includes fixed-width integer types and exposes constants for the 8-byte VXLAN header, the 3-byte VXLAN network identifier, the VNI-present flag, and the shift used to position/extract the VNI field.

`vxlan_hdr_t` is packed to match the network header layout exactly. It contains a 32-bit flags word and a 32-bit VNI/reserved word. `VXLAN_F_VDI` is the standard VXLAN valid-network-ID flag bit, and `VXLAN_ID_SHIFT` accounts for the reserved low byte in the VNI field.

The file is intentionally small and shared by VXLAN implementation code that needs stable packet-format definitions.
