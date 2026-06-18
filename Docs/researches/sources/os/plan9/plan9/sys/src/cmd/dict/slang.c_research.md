# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/slang.c

Implements the English Slang dictionary backend for a tagged line format. Tags are two-letter keys followed by a space: `me`, `df`, `dx`, `et`, `ex`, `la`, `nu`, `pr`, `ps`, `xr`, and `xx`.

`slangprintentry` uses `sget` to find the next tagged value region. Headword mode prints only the first `ME` tag. Full mode formats each tag type into plain text: definitions and examples with periods, etymology and pronunciation in brackets, labels in parentheses, sense numbers as indented numbered sections, parts of speech as indented labels, and cross references as `See ...`.

`slangnextoff` scans for a line beginning `me `. `sget` finds the next recognized tag line and returns the value range up to the following tag or entry end. `soutpiece` emits a value while changing newlines to spaces, coalescing repeated spaces, and dropping `@`.

Integration points: registered as `slang` in `utils.c`.

Risks and notes: unknown two-letter tag-looking lines can produce debug diagnostics and are skipped. The parser assumes `*e == 0` per its comment, so entry construction must provide a terminating byte.
