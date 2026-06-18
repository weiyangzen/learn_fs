# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/format.h

## Role

`private/format.h` declares internal helpers for FLAC format calculations and partitioned Rice coding contents management.

## API Surface

It declares functions to compute maximum Rice partition order from blocksize, predictor order, and optional limits. It also declares init, clear, and ensure-size helpers for `FLAC__EntropyCodingMethod_PartitionedRiceContents`.

## Risks / Edge Cases

The partition-order helpers encode FLAC format constraints that must stay consistent with encoder residual partitioning. Incorrect limits can produce invalid subframes or inefficient encoding.

## Dependencies

Includes public `FLAC/format.h`.
