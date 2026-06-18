# sources/test-tools/strace/src/random_ioctl.c

Purpose: Decodes random-device ioctls such as entropy count and entropy injection.

Important APIs/types/functions: `random_ioctl` and `struct rand_pool_info` handling.

Control flow: `RNDGETENTCNT` prints output integer on exit; `RNDADDTOENTCNT` prints input integer; `RNDADDENTROPY` fetches `rand_pool_info`, prints entropy count and buffer size, then prints the variable buffer pointer/data according to common string/hex helpers; unhandled commands return generic decoded status.

State and persistence: stateless; does not modify traced data.

Dependencies/integration: `<linux/random.h>`, random ioctl xlat, `printnum_int`, `umove_or_printaddr`, and generic ioctl dispatcher.

Risks: variable-length entropy buffer must be bounded by the struct field and tracee memory availability. `RNDGETPOOL` historical behavior is noted but not deeply decoded.

Test signals: ioctl tests for entropy count get/add, entropy add with short/invalid pointers, and unknown random ioctls.
