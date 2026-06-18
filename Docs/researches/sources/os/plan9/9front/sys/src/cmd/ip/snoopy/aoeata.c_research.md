# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoeata.c

This module decodes the AoE ATA command payload. It defines fields for ATA flags, command/status, features/error, sector count, and 48-bit LBA.

`llba` converts the six-byte little-endian AoE LBA into a `uvlong`. `p_filter` compares parsed fields and notes that status/error matching is direction-blind because the dissector lacks request/response context. `p_seprint` prints ATA flag, err/feat, sector count, cmd/status, and LBA, then terminates protocol traversal.

The module is a leaf `Proto aoeata`.
