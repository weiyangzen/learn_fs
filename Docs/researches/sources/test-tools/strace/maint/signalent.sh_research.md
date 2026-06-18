# sources/test-tools/strace/maint/signalent.sh

Purpose: converts signal `#define SIG... <number>` lines into indexed signal-name table entries.

Important APIs/types/functions: pipeline of `cat`, `sed`, numeric sort/uniq, and awk formatting with placeholder names for gaps.

Control flow: strip comments, extract signal names and numbers, sort by number, skip duplicates, emit `"SIG_<n>"` placeholders for missing numeric slots up to each found signal, then emit the named signal entry aligned with tabs. It ignores signals above 256.

State and persistence behavior: stdout only.

Dependencies and integration points: used to generate architecture signal tables for strace's signal decoding.

Risks: only simple numeric defines are recognized; aliases and macro expressions are skipped. The awk assignment `n` appears duplicated but harmless.

Test signals: generated signal tables should include expected arch signal names and placeholders, and signal decoding tests should resolve common signals.
