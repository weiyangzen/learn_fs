# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/readlist.c

Purpose: batch Venti block read checker for score/type lists.

Behavior:
- Reads from stdin or named files.
- Each line must contain a hex score and numeric type.
- `parsescore` manually decodes 40 hex characters into a 20-byte score.
- `run` reads each listed block and prints progress every 1000 reads; raw output is intentionally commented out.

Integration points:
- Uses `Bio` for input and Venti `vtread`.

Risks:
- Exits fatally on first syntax/read error.
- Does not close Venti connection explicitly before thread exit.
