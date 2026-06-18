# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rc4.c

Implements RC4 key scheduling and stream operations. It includes `os.h` and `<libsec.h>`.

`setupRC4state` initializes the 256-byte permutation and performs the key-scheduling algorithm over the supplied key bytes. `rc4` applies the PRGA to XOR keystream into a buffer in place and updates `x`/`y` indices in the state.

`rc4skip` advances the PRGA without emitting bytes. `rc4back` reverses the PRGA state by undoing swaps and index movement for a requested number of bytes, allowing the stream position to move backward.
