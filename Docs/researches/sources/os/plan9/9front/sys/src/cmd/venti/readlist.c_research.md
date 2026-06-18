# File Research: sources/os/plan9/9front/sys/src/cmd/venti/readlist.c

Purpose: Batch Venti block reader for lists of score/type pairs.

Key behavior:
- Reads one or more files, or stdin, containing two fields per line: hex score and type.
- Parses exactly 40 hex score characters into a 20-byte score.
- Reads each listed block from the Venti server.
- Prints progress every 1000 reads; payload writing is present but commented out.

Dependencies:
- Uses Venti read APIs and Plan 9 `Biobuf`.

Notable details:
- This is mainly a cache/server stress or validation utility, not a data extraction tool in its current form.
