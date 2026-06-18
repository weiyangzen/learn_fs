# File Research: sources/virtualization/nbdkit/plugins/ondemand/default-command.sh.in

## Purpose
Defines the default shell command embedded into the `ondemand` plugin for creating a new filesystem image.

## Main Flow
Defaults `type` to `ext4`, chooses mkfs options and label flag by filesystem type, truncates `$disk` to `$size`, then invokes `mkfs -t "$type"` with optional label support.

## Dependencies
Requires shell, `truncate` substituted as `__TRUNCATE__`, and an appropriate `mkfs` implementation for the selected filesystem type.

## Risks and Notes
The script uses shell variables supplied by the plugin, so command construction must quote user-provided values correctly. Filesystem-specific option mapping is intentionally small and may not cover all mkfs implementations or filesystem types.
