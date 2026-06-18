# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.c

- Role: Command-line tool for reading, writing, and dumping message token databases.
- Behavior: Opens DB with optional create; in input mode reads `token [value]` lines and updates counts; otherwise enumerates all key/value pairs.
- Integration: Front-end for `Msgdb` implementation in `msgdbx.c`.
- Risks/notes: `-i` is accepted but omitted from usage text.
