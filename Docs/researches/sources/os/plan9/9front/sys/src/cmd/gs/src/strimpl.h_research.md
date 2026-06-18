# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/strimpl.h

Definitions for stream implementors.

Key points:
- Documents the `process` procedure contract in detail.
- Process return values:
  - `EOFC`: end of data
  - `ERRC`: syntax/error
  - `0`: need more input
  - `1`: need more output space
- Explains special `last = 1` handling for encoders when no more input will arrive.
- Documents stricter EOD/read-ahead behavior required for decoding filters.
- Notes that decoders requiring explicit EOD should set `min_left = 1`.
- Defines `stream_template_s` fields:
  - state descriptor
  - init procedure
  - process procedure
  - minimum input/output sizes
  - release procedure
  - parameter/default pointer initializer
  - reinit procedure
- Declares `stream_move`.
- Declares `s_hex_process` and `hex_syntax`.

Dependencies and interactions:
- Includes `scommon.h`, `gstypes.h`, and `gsstruct.h`.
- Used by all concrete stream filters and by `stream.c`.

Research relevance:
- This is the implementor-facing contract that keeps all filters compatible with Ghostscript’s pipeline engine.
