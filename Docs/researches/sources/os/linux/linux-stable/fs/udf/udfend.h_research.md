# File Research: sources/os/linux/linux-stable/fs/udf/udfend.h

## Summary
Provides endian conversion helpers between little-endian UDF on-disk address descriptors and CPU-native kernel structures.

## Main Responsibilities
- Converts logical block addresses between `lb_addr` and `kernel_lb_addr`.
- Converts short allocation descriptors between little-endian and CPU forms.
- Converts long allocation descriptors between little-endian and CPU forms.
- Converts extent descriptors to CPU form.

## Important Behavior
The helpers intentionally return whole converted structs, keeping call sites concise and avoiding partial endian conversion.

## Risks
These helpers are small but foundational. Incorrect conversion would mis-map extents, partition references, descriptor locations, and metadata address fields across the whole UDF driver.
