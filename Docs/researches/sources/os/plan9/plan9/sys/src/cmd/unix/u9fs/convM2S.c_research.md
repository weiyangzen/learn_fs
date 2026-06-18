# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2S.c

Parses 9P wire messages into an `Fcall`.

Major helpers:
- `gstring` reads a counted string, shifts bytes down over the length field, appends NUL, and returns an in-buffer string pointer.
- `gqid` reads a serialized `Qid`.

`convM2S` behavior:
- Validates size/type/tag framing.
- Switches across T/R message types including version, flush, auth, attach, walk, open, create, read, write, clunk, remove, stat, wstat, error, and replies.
- Bounds-checks fixed fields, counted data, string extents, stat payloads, qid arrays, and MAXWELEM counts.
- Returns the message size only if parsing consumes exactly the declared size.

Notable behavior:
- Contains commented-out older/session auth message variants.
- Mutates the input buffer when converting strings to NUL-terminated in-place strings.
