# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/words/dumpvacroots

Purpose: RC script to extract historical vac root scores from a Venti server.

Key behavior:
- Derives an HTTP host/port from `$venti`.
- Fetches `/index`, generates `venti/printarena` commands for arena ranges, executes them, and filters clumps of type `16` into `vac:<score>` output.

Dependencies:
- Uses `hget`, `sed`, `awk`, `rc`, and `venti/printarena`.

Notable details:
- Comment warns that physical disk access exposes stored vac roots.
