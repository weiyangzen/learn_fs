# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifrpred.h

Declares read-side predictor filter helper.

Key points:
- Exports `filter_read_predictor` from `zfdecode.c` for `zfzlib.c`.
- Signature takes interpreter context, operand pop count, stream template, and stream state.

Research relevance:
- Shared hook for composing read filters with PNG/TIFF predictor processing.
