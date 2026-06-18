# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgbuf.h

Kernel message buffer ring metadata for console/log output.

Key responsibilities:
- Defines `struct msgbuf` with magic, buffer size, write/base/read indices, backing pointer, and reserved field.
- Defines current and old magic constants: `MSG_MAGIC` and `MSG_OMAGIC`.
- Declares kernel globals `msgbuftrigger` and `msgbufp`.
- Declares `msgbufinit()`.
- Provides default `MSGBUF_SIZE` of 1 MiB if not configured.

Important behavior:
- Indices are not masked when stored; accessors must mask against `msg_size` to get physical buffer offsets.
- Unsigned arithmetic allows relative distance calculation by subtraction.

Dependencies:
- Includes `sys/types.h`.
- Kernel consumers are console/logging and message-buffer initialization code.

Notable risks:
- Any accessor that forgets to mask indices can address outside the ring.
- Ring index wraparound assumptions depend on unsigned integer behavior.
