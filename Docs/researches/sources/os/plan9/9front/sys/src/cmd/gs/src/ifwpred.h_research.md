# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifwpred.h

Declares write-side predictor filter helper.

Key points:
- Exports `filter_write_predictor` from `zfilter2.c` for `zfzlib.c`.
- Signature mirrors read predictor setup: context, pop count, stream template, and stream state.

Dependencies and interactions:
- Used by encoded output filters that need predictor preprocessing.

Research relevance:
- Small shared hook for composing write filters with predictor processing.
