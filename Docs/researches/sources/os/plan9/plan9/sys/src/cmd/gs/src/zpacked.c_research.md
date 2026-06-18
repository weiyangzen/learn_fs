# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpacked.c

Packed-array operators and packed-array construction. It implements `currentpacking`, `packedarray`, and `setpacking`, plus exported helper `make_packed_array`.

`currentpacking` returns the current global packing flag. `setpacking` stores a new boolean into the packing container with the correct old-reference write barrier. `zpackedarray` validates the requested element count, temporarily removes the count operand, and calls `make_packed_array`.

`make_packed_array` performs a two-pass conversion from stack refs to packed storage. The first pass computes required packed/full-ref storage and checks local-into-global stores. The second pass encodes packable names, small integers, and executable operators into short packed refs, expands runs when a full ref must be aligned, pads with legal packed integer refs for GC scanning, pops source operands, and returns either a `t_shortarray` or `t_mixedarray`. Alignment and GC safety are the main invariants.
