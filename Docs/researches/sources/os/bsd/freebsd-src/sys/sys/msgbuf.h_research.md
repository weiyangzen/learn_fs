# File Research: sources/os/bsd/freebsd-src/sys/sys/msgbuf.h

Defines kernel circular message buffer state and APIs.

Key content:
- `struct msgbuf` stores buffer pointer, magic value, size, write/read sequence numbers, checksum, sequence modulus, last priority, flags, and mutex.
- Magic constant `MSG_MAGIC`.
- Flags:
  - `MSGBUF_NEEDNL`
  - `MSGBUF_WRAP`
- Sequence macros normalize sequence values, convert sequence to buffer position, and add/subtract normalized sequence numbers.
- Kernel declarations include global msgbuf size/trigger/pointer and global lock.
- Kernel APIs initialize, reinitialize, duplicate, clear, copy, add char/string, get bytes, peek bytes, get count, and get one character.
- Default `MSGBUF_SIZE` is `32768 * 3` unless overridden.

Research relevance:
- Kernel log/message ring used for boot/runtime diagnostics.
- Relevant to filesystem research for crash/debug output and persistent diagnostic paths.

Cautions:
- Sequence arithmetic uses `msg_seqmod`, not raw buffer size, to handle wrap behavior.
- Includes lock/mutex headers and embeds a mutex in the message buffer.
