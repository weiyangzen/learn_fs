# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.h

## Purpose
Defines internal inflate state and mode enumeration.

## Key Elements
Defines `GUNZIP` unless `NO_GZIP` is set, the `inflate_mode` enum, and `struct inflate_state`. State includes wrapper flags, check values, total output, sliding-window metadata, bit accumulator, copy length/distance fields, dynamic-code counters, temporary length arrays, work arrays, and `codes[ENOUGH]`.

## Behavior/Risks
This is not public API. The mode enum encodes resumable inflate progress across calls, including gzip header sub-states, dictionary wait, block decode states, trailer checks, and error/sync states. The structure is shared by normal and callback-based inflate, so layout coupling is strong.

## Dependencies
Requires `code` and `ENOUGH` from `inftrees.h`, plus zlib integer and pointer types from included configuration headers.
