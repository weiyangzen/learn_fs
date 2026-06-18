# File Research: sources/os/plan9/plan9/sys/src/cmd/bsplit.c

Plan 9 `bsplit`, a copy-light binary splitter.

Options:

- `-p pfx`: output filename prefix, default `bs.`
- `-s size`: maximum output size, default 512 MiB
- `-d`: increments debug flag but does not otherwise affect processing

It reads stdin or listed files into a 128 KiB buffer and writes sequential files named `<prefix><5-digit-number>`. The output loop tries to write sector-aligned chunks when possible, closes the current output when it reaches the size limit, and continues until all inputs are consumed.
