# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regcomp.c

Regex compiler for Henry Spencer-style POSIX regexes with NetBSD/FreeBSD updates, GNU extension support, wide-character handling, and Boyer-Moore optimization metadata.

Important responsibilities:
- `regcomp_internal()` allocates parse/guts state, chooses BRE vs ERE parser, emits the strip, compacts it, finds mandatory literals, computes jump tables, counts plus nesting, and populates `regex_t`.
- `p_ere_exp()`, `p_simp_re()`, and `p_re()` parse ERE/BRE atoms, concatenation, branches, anchors, groups, backreferences, and repetitions.
- Bracket parsing supports character classes, equivalence classes, collating symbols, ranges, case-insensitive sets, word-boundary special cases `[[:<:]]` and `[[:>:]]`, and GNU pseudo-classes `\w`, `\W`, `\s`, `\S`.
- `repeat()` lowers bounded repetition into strip operations by duplication and optional/plus constructs.
- `findmust()`, `computejumps()`, and `computematchjumps()` derive literal substrings and Boyer-Moore skip tables for `regexec()`.
- `allocset()`, `CHadd()`, `CHaddrange()`, and `CHaddtype()` build cset data for `OANYOF`.

The compiled representation is a strip of `sop` operators. The file is careful about allocation growth with `reallocarray()`, large pattern size overflow, and preserving the first parse error. It uses `REG_GNU` when enabled and `PFLAG_LEGACY_ESC` internally for escape behavior.
