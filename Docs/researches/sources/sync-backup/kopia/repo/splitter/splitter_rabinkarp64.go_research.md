# sources/sync-backup/kopia/repo/splitter/splitter_rabinkarp64.go

Purpose: implements content-defined chunking with a 64-bit Rabin-Karp rolling hash.

Important APIs/types/functions: `rabinKarp64Splitter` mirrors the BuzHash splitter with `rabinkarp64.RabinKarp64`, `mask`, `count`, `minSize`, and `maxSize`. Methods implement the splitter interface. `newRabinKarp64SplitterFactory(avgSize)` configures min/max/mask.

Control flow: reset seeds a zero window. `NextSplitPoint` fast-forwards until minimum size, then rolls each byte looking for `Sum64()&mask == 0`, or forces a split at max size.

State and persistence behavior: in-memory rolling hash state; splitter choice affects persisted chunk layout and dedup opportunities.

Dependencies/integration: depends on `github.com/chmduquesne/rollinghash/rabinkarp64`; registered under `DYNAMIC-*-RABINKARP` algorithms.

Risks: the file comment says not using Hash32 although this is 64-bit; the rationale is still interface-dispatch performance. As with BuzHash, average size must align with mask assumptions and off-by-one changes are format-affecting for chunk boundaries.

Test signals: splitter stability tests assert exact split statistics for Rabin-Karp sizes and feeding modes, including pooled reuse.
