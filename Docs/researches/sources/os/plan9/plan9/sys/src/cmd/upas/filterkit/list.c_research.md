# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/list.c

- Role: Address-list checker/updater for mail filtering.
- Control flow: Reads pattern files with exact (`=`), regexp (`~`), negated (`!`) entries and `#include`; `check` tests address files; `add` simplifies unmatched addresses and appends patterns.
- Key helpers: `simplify` lowercases and reduces domains to broad regexp patterns; `checkaddr` compiles regexes as needed.
- Integration: Uses `readaddrs`, Plan 9 regexp, String, quoting formatter, and libsec includes.
- Risks/notes: Regexes are compiled on every check rather than cached; source contains offensive comment text unrelated to behavior.
