# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desmodes.c

Provides DES state initialization wrappers `setupDESstate` and `setupDES3state`. It includes `os.h` and `<libsec.h>`.

`setupDESstate` zeroes the state, copies the 8-byte key, expands it with `des_key_setup`, copies an optional IV, and sets `setup = 0xdeadbeef`. `setupDES3state` repeats the same pattern for three 8-byte keys and three expanded schedules.

The file documents that these routines use the 64-bit DES key format; older 56-bit key compatibility lives in `des.c`.
