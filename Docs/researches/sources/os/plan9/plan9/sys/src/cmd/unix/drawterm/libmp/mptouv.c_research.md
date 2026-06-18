# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptouv.c

Provides unsigned `uvlong` conversion helpers `uvtomp(uvlong v, mpint *b)` and `mptouv(mpint *b)`. `VLDIGITS` is computed as `sizeof(vlong)/sizeof(mpdigit)`, and the code assumes a `vlong` is an integral number of `mpdigit`s.

`uvtomp` ensures enough space for all native long limbs, clears the destination, then emits low-to-high `mpdigit` chunks until `v` becomes zero. `mptouv` normalizes the input, returns `0` for empty magnitude, returns `MAXVLONG` when too many limbs are present, and reconstructs a native value by shifting each limb to its native offset.

The function ignores negative sign for normal in-range values; it treats the stored magnitude as unsigned. Overflow handling uses `MAXVLONG` rather than `MAXUVLONG`, which is a compatibility/convention detail worth preserving.
