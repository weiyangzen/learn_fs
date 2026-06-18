# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srlx.h

Shared header for RunLength encode/decode filters.

Key contents:
- Defines common `EndOfData` parameter.
- Defines `stream_RLE_state` with `record_size`, `record_left`, and delayed literal copy count.
- Provides RLE default/init macros, with zero `record_size` normalized to `max_uint`.
- Defines `stream_RLD_state` with delayed output count and repeat/literal indicator.
- Provides RLD default/init macros, including `min_left` setup based on `EndOfData`.
- Declares encode and decode templates.

Notable dependencies:
- Requires stream common definitions.

Research notes:
- Both filters expose inline init macros so clients can avoid procedure-call overhead.
