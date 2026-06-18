# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifrpred.h

Declares read-side predictor filter helper.

Key points:
- Exports `filter_read_predictor` from `zfdecode.c` for `zfzlib.c`.
- Signature takes interpreter context, operand pop count, stream template, and stream state.

Dependencies and interactions:
- Used by Flate/zlib decode paths that need PNG/TIFF predictor wrapping.

Research relevance:
- Small shared hook for composing read filters with predictor processing.
