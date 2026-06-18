# sources/sync-backup/git-lfs/ssh/protocol.go

Purpose: implements the Git LFS SSH pkt-line protocol framing, version negotiation, command sending, and status/data/line response parsing.

Important APIs/types/functions: `PktlineConnection`, `Lock`, `Unlock`, `Start`, `End`, `negotiateVersion`, `SendMessage`, `SendMessageWithLines`, `SendMessageWithData`, `ReadStatus`, `ReadStatusWithData`, and `ReadStatusWithLines`.

Control flow: `Start` negotiates `version=1`: read capabilities, send `version 1`, then require status 200. Send methods write a command, args, optional delimiter plus lines/data, then flush. Read methods require the first packet to be `status NNN`, collect args before a delimiter, then either return a streaming data reader or text lines until flush.

State/persistence behavior: connection state consists of stdin/stdout pipes, subprocess, mutex, and pktline wrapper. `End` sends `quit`, reads status, closes pipes, and waits for the process.

Dependencies/integration: used by SSH transfer and SSH lock client. Depends on `subprocess.Cmd`, translated protocol errors, and pktline framing semantics.

Risks: callers of `ReadStatusWithData` must exhaust the returned reader before further reads. `SendMessageWithData` stops on any read error and then flushes without distinguishing EOF from non-EOF errors, so upstream readers should be reliable.

Test signals: failures appear as protocol errors during SSH transfer, lock commands, or version negotiation.
