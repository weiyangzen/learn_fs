# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter.h

Header defining stream states for simple Ghostscript filters: eexec encode/decode, PFB decode, and SubFileDecode.

Key contents:
- `stream_exE_state` stores the Type 1 encryption state for eexec encoding.
- `stream_exD_state` stores eexec decode parameters and dynamic state: crypt state, binary/hex detection, `lenIV`, optional underlying PFB state pointer, odd hex digit, remaining PFB record/hex counts, and skip count.
- `stream_PFBD_state` stores PFB record decode mode, record type, and record bytes left.
- `stream_SFD_state` stores SubFileDecode limits, EOD pattern, skip count, match state, and delayed-copy state.

Notable dependencies:
- Uses Ghostscript stream and GC declaration macros.
- Requires `gstypes.h`; comments note historical compiler issues around `strimpl.h`.

Research notes:
- This is a state-contract header; implementations are split across `seexec.c` and `sfilter1.c`.
- The state layouts expose client-set parameters separately from initialization-derived and dynamic values.
