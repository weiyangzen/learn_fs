# File Research: sources/os/plan9/9front/sys/src/cmd/dict/slang.c

Adapter for the English Slang dictionary format.

Key elements:
- Recognizes two-letter line tags: definition, examples, etymology, labels, main entry, sense number, pronunciation, part of speech, and cross references.
- `slangprintentry` formats tagged pieces into readable prose; `h` mode prints only the main entry.
- `slangnextoff` finds entries beginning with `me `.
- `sget` parses the next recognized tagged value and returns its range.
- `soutpiece` normalizes newlines/spaces and drops `@` characters.

Dependencies:
- Uses `Assoc` lookup and common output helpers.

Research notes:
- Unknown tags can be reported under debug mode.
