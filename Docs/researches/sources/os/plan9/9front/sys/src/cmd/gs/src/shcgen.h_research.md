# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/shcgen.h

Declares the Huffman generation API implemented by `shcgen.c`.

Key points:
- Exposes `hc_compute` for frequency-to-definition generation.
- Exposes byte-string conversion helpers for compact serialized definitions.
- Exposes encode table generation and decode table size/generation helpers.
- Requires callers to allocate `hc_definition` count/value arrays before reconstruction.

Research relevance:
- This is the public interface for building canonical Huffman tables from dynamic or serialized data.
