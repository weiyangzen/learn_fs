# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_store.h

`vuid_store.h` is the private implementation header for VUID state storage. It backs the opaque state type exposed by `vuid_state.h` and is tuned for compact storage of mostly-boolean input state with a small number of integer-valued input codes.

The comments describe the typical state layout: a VKEY segment containing location absolute/delta values, plus an ASCII/meta segment of boolean values. The package knows how to keep absolute and delta location values related, so mouse or locator movement can update complementary state. The storage design optimizes for high-volume mouse tracking and grouped checks of modifier/shift-button state.

`Vuid_value` is a linked-list node for one non-boolean VUID value, storing a segment-relative offset and integer value. `Vuid_seg` is a linked-list node for a VUID segment. It stores the segment base address, a bit array for boolean state, a parallel bit array indicating which offsets are integer-backed, and a linked list of `Vuid_value` nodes for those integer values. Segment and value lists are deliberately unsorted unless profiling shows a need.

The bit manipulation macros operate on segment-relative offsets and use a most-significant-bit-first convention within each byte. They set, clear, and test the boolean-state array and the integer-presence array. `vuid_cstate_to_state()` casts the opaque client state to the private `Vuid_seg *` representation.

Key dependencies are the VUID segment sizing constants such as `VUID_SEG_SIZE`, supplied by the VUID event namespace headers. The main correctness risk is that callers must keep offsets within segment bounds; the macros perform no bounds checking.
