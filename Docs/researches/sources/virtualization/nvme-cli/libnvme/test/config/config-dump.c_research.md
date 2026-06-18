# File Research: sources/virtualization/nvme-cli/libnvme/test/config/config-dump.c

## Purpose
Small test binary that scans topology, reads a JSON config, and dumps the merged config.

## Behavior
Creates a global context, scans topology while tolerating `-ENOENT`, reads the supplied config file, dumps JSON config to stdout, and exits success/failure.

## Relevance
Used by fixture diff tests to validate JSON import/export and sysfs-discovered topology merging.
