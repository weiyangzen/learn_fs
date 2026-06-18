# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifwpred.h

Declares write-side predictor filter helper.

Key points:
- Exports `filter_write_predictor` from `zfilter2.c` for `zfzlib.c`.
- Signature mirrors read predictor setup: context, pop count, stream template, and stream state.

Research relevance:
- Shared hook for encoded output filters that need predictor preprocessing.
