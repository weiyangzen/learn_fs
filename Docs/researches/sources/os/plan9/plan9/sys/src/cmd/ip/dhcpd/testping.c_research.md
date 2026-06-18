# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testping.c

`testping.c` is a tiny ICMP probe test wrapper.

Key behavior:
- Initializes IP formatters.
- Exits silently without an argument.
- Calls `icmpecho(argv[1])` and prints whether the address answers.

Important dependencies:
- Includes `dat.h` and defines `blog` for `ping.c`.

Notable risks/quirks:
- Passes `argv[1]` directly to `icmpecho`, whose signature expects `uchar *` IP bytes, so this test appears type-inconsistent unless built with a different declaration context.
