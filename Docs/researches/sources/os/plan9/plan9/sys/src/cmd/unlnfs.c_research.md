# File Research: sources/os/plan9/plan9/sys/src/cmd/unlnfs.c

- Role: Restores long filenames from LNFTS-style encoded names using `.longnames`.
- Control flow: Reads long names, computes 26-character base32 MD5 short names, recursively scans directories, and renames matching encoded entries to long names via `dirwstat`.
- Key functions: `long2short`, `readnames`, `renamedir`, and `rename`.
- Integration: Uses Plan 9 `libsec` MD5 and base32 encoding.
- Risks/notes: Recurses through all directories before renaming matching entries; duplicate hash-derived names would collide.
