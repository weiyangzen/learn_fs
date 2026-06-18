<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_random.c -->
# sources/test-tools/strace/tests/ioctl_random.c

Purpose: tests random-device ioctl decoding for entropy counters, entropy addition, pool reset/clear/reseed, and unknown random ioctl commands.

Important APIs/types/functions: Uses `linux/random.h`, `struct rand_pool_info`, `RNDGETENTCNT`, `RNDADDTOENTCNT`, `RNDADDENTROPY`, `RNDZAPENTCNT`, `RNDCLEARPOOL`, `RNDRESEEDCRNG`, and `xlat/random_ioctl_cmds.h`.

Control flow: initializes a `rand_pool_info` union with `entropy_count=3`, `buf_size=8`, and buffer `"12345678"`, then calls each random ioctl on fd `-1`, printing pointer or dereferenced argument forms. It finishes with an unknown `_IO('R', 0xff)` command.

State and persistence behavior: no random pool state is modified due to invalid fd; only local union and integer state exist.

Dependencies/integration points: validates strace random ioctl xlat tables and variable-length `rand_pool_info` decoding.

Risks and test signals: command aliases can affect names. Passing output confirms entropy buffer decoding, pointer classification, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_random.c -->
