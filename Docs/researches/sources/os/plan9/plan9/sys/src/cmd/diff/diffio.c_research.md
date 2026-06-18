# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffio.c

Input, hashing, verification, and change-output layer for regular-file `diff`.

`readline` reads one logical line into a 4096-byte buffer, truncating overlong lines after consuming the rest. `readhash` computes the historical 7-bit/16-bit one’s-complement line hash, with `bflag` modes for exact, coalesced whitespace, or whitespace-stripped comparison.

`prepare` opens a file, detects likely binary data by sampling runes, builds the per-line hash array, records input buffers and file names, and sets `binary` if needed. `check` rereads both files using the match vector `J` from `diffreg.c`, computes line offsets (`ixold`, `ixnew`), and invalidates hash-collision matches after comparing actual line text with whitespace policy applied.

`change` emits one edit hunk in normal, ed-script, reverse-script, `-n`, or buffered context/all-context modes. `fetch` prints saved source ranges using line-offset arrays. `flushchanges` groups buffered context changes with three lines of context, or prints entire files for mode `a`.

Integration points: `diffreg.c` produces `J`, then calls `check` and `output`/`change`; `main.c` controls flags.

Risks and notes: lines longer than 4095 bytes are truncated for textual diffing. Binary detection is heuristic. Context buffering uses a global dynamically grown array and fixed three-line context.
