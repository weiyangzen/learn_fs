# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/roget.c

Implements callbacks for Project Gutenberg Roget’s Thesaurus plain-text format.

`rogetprintentry` has separate behavior for headword-only and full output. Headword mode skips the numeric class prefix, bracketed/brace sections, punctuation, and digits until the first ` -- ` delimiter, emitting a cleaned phrase. Full mode skips the numeric prefix, treats ` -- ` as a major break, cleans continuation lines, rewrites useful `&c (...)` cross references as slash-delimited references, suppresses less useful `&c` numeric references, and normalizes spacing before punctuation.

`rogetnextoff` scans line by line for a line beginning with a digit and containing ` -- `, returning that line’s offset. `rogetprintkey` has no key.

Integration points: registered as `roget` in `utils.c`.

Risks and notes: format detection is heuristic and line-oriented. There is a stale `Last` global that is not used. One string comparison checks `p < e.end -2` but compares four bytes, so malformed very short tails could be fragile, though normal dictionary records likely avoid this.
