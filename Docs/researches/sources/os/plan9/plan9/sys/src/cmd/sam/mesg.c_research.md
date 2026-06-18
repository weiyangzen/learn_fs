# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.c

Implements the host side of the `sam`/`samterm` binary message protocol.

Key responsibilities:
- Receives terminal-originated `Tmesg` records from stdin with a 3-byte header and dispatches in `inmesg`.
- Handles terminal requests for file starts, edits, cut/paste/snarf, search, write/close, double-click, plumbing, and shutdown.
- Maintains host-side protocol buffers: `indata`, `outdata`, `inp`, `outp`, `outmsg`, `waitack`, `outbuffered`, and terminal protocol version `tversion`.
- Serializes host-originated `Hmesg` messages with helpers such as `outTs`, `outTslS`, `outTsll`, `outTsv`, and `outflush`.

Behavior notes:
- Flow control uses `Hack`/`Tack`: buffered output is flushed by sending `Hack` and reading until `Tack`.
- `Trequest` fills terminal rasp holes by finding available spans with `rdata` and sending `Hdata`.
- `Ttype`, `Tcut`, and `Tpaste` update file logs, file sequence state, terminal dot assumptions, and command execution when command text ends in newline.
- `Tstartsnarf`/`Tsetsnarf` bridge the internal rune snarf buffer and terminal snarf exchange, capped by `SNARFSIZE`.
- `Tplumb` builds a Plan 9 `Plumbmsg` from the selected text or clicked word and sends packed data back via `Hplumb`.

Risk/maintenance notes:
- Message parsing uses static receiver state, global buffers, and panics on malformed lengths.
- Many protocol paths assume valid file tags and call `hiccough`/`panic` on mismatch.
