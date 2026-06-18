# File Research: sources/os/plan9/9front/sys/src/cmd/upas/dkim/dkim.c

This command signs a mail message from stdin with a DKIM-Signature header written to stdout.

Key behavior:
- Signs selected headers: from, to, subject, date, message-id.
- Reads headers, strips existing `DKIM-Signature:`, canonicalizes lines with CRLF, and hashes selected headers.
- Reads body, suppressing extra trailing blank lines per simple canonicalization behavior.
- Computes SHA-256 body hash, constructs a DKIM header with `rsa-sha256` and `simple/simple`, hashes it with selected headers, and signs via factotum RPC.
- Writes DKIM header, original headers, blank line, then body.
- Options: `-d domain` required, `-s selector` optional default `dkim`.

Integration and risks:
- Uses factotum key spec `proto=rsa service=dkim role=sign hash=sha256 domain=...`.
- `usehdr` uses `realloc(*hs, strlen(*hs)+strlen(*p)+1)` then `strcat`, which leaves no separator and appears short by one if multiple header names are concatenated without accounting for previous NUL only; current behavior deserves caution.
- Header continuation handling signs continuations only while `use` remains set.
