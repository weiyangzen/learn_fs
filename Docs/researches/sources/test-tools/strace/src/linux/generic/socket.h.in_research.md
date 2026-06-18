# sources/test-tools/strace/src/linux/generic/socket.h.in

Purpose: build-time wrapper template around `<linux/socket.h>` that supplies `sockaddr_storage` as `__kernel_sockaddr_storage` when the kernel header does not expose the expected name.

Important APIs/types/functions: exports preprocessor compatibility for `sockaddr_storage`; no functions or runtime structs are implemented locally.

Control flow: the generated wrapper uses `#include_next <linux/socket.h>` to keep the real kernel header in the chain, then defines the missing compatibility name when needed.

State/persistence behavior: build-time header compatibility only; no runtime state is introduced.

Dependencies/integration: supports socket/network syscall decoders and headers that expect Linux socket UAPI definitions while also satisfying libc-facing `sys/socket.h` assumptions.

Risks/test signals: include-order mistakes can hide real kernel socket definitions or leave `sockaddr_storage` undefined; test generated-header compilation of socket decoders and sockaddr printers.

Source-read signal: reviewed complete local file (7 lines).
