# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/readaddrs.c

- Role: Reads address tokens from a file into an `Addr` linked list.
- Key functions: `tokenize822` splits on whitespace while respecting double quotes; `readaddrs` reads up to 8 KiB, tokenizes, appends newly allocated address nodes.
- Integration: Shared by filterkit list and deliver tools.
- Risks/notes: Reads only the first 8 KiB of the address file.
