# File Research: sources/os/linux/linux/block/partitions/of.c

## Summary
Creates block partitions from device-tree `fixed-partitions` nodes.

## Main Responsibilities
- Checks whether the disk device node is compatible with `fixed-partitions`.
- Validates each child `reg` property before adding any partitions.
- Converts byte offsets and sizes to 512-byte sectors.
- Applies `read-only` partition flags.
- Stores partition labels from `label` or `name`.

## Key API
- `of_partition()`.

## Important Behavior
Validation requires the `reg` length to match address and size cell counts, offset to be sector-aligned, and size to be nonzero and sector-aligned. The parser performs a full validation pass first, then a second pass that adds partitions.

## Risks
The implementation assumes the disk device node itself is the `fixed-partitions` node. Partition label handling assumes a usable `label` or `name` property is present.
