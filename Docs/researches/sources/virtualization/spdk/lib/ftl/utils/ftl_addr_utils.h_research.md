# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_addr_utils.h

Inline helpers for reading/writing packed or unpacked FTL address/LBA arrays.

Behavior:
- If `ftl_addr_packed(dev)` is true, loads/stores 32-bit values and maps 32-bit invalid sentinels to full invalid constants.
- Otherwise uses 64-bit arrays directly.
- Provides symmetric helpers for `ftl_addr` and LBA values.

Risk:
- Store paths assign potentially 64-bit invalid values into 32-bit slots when packed; correctness depends on invalid constants being intentionally compatible.
