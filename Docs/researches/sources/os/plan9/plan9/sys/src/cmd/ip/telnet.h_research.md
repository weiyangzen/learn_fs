# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.h

Shared TELNET protocol constants, option table, and negotiation helpers.

Key behavior:
- Defines TELNET command bytes and option numbers.
- Defines `Opt` with name, code, refusal flag, change/subnegotiation callbacks, and local/remote state.
- Implements control dispatch for IAC commands: WILL, WONT, DO, DONT, SB, AYT, SE.
- Negotiates option state and sends reciprocal replies.
- Parses subnegotiation payloads and invokes option-specific handlers.
- Provides robust read/write wrappers that handle interrupted syscalls, note sending, simple fatal/error helpers, and debug output.

Integration:
- Included directly by both telnet client and telnet daemon.
- Expects including file to provide `Biobuf`, `debug`, and option callback configuration.

Risks and notes:
- Header contains function definitions and global `opt[]`, so it is intended for direct inclusion into individual binaries, not normal shared compilation.
- `sub()` silently truncates subnegotiation payloads longer than 128 bytes.
