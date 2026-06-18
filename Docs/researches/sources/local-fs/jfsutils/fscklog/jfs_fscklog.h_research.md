# File Research: sources/local-fs/jfsutils/fscklog/jfs_fscklog.h

Shared control structure and constants for fsck log extraction/display.

Key contents:
- Includes `fscklog.h`.
- Defines `struct fscklog_record`, carrying:
  - On-device fsck workspace and fsck log byte/block offsets and lengths.
  - Input/output buffer pointers, sizes, current offsets, and data lengths.
  - Input aggregate/log offsets.
  - Last output message header pointer.
  - Aggregate block size.
  - State flags for selected log, open device/file streams, buffer state, EOF, and filename selection.
  - Highest fsck message number.
- Defines default extracted log filenames `fscklog.new` and `fscklog.old`.
- Defines `NEWLOG` and `OLDLOG`.
- Defines module return codes for display/extract failures.
- Declares `xchklog()` and `xchkdmp()`.

Interactions:
- Central state passed from `fscklog.c` into extraction/display modules.
- Buffers and offsets are initialized differently by `extract.c` and `display.c`.

Research notes:
- This struct is global-state oriented and mixes device-layout state with file I/O state.
