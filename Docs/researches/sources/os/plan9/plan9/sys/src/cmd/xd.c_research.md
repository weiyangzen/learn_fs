# File Research: sources/os/plan9/plan9/sys/src/cmd/xd.c

This is a flexible binary dump utility.

Options:
- `-u`: flush output after each line.
- `-r`: collapse repeated 16-byte lines to `*`.
- `-s`: swizzle each group of four bytes.
- `-a{o|d|x}`: address base octal/decimal/hex.
- Format specs: `-c`, `-R`, or combinations of size `{b,1,w,2,l,4,v,8}` and base `{o,d,x}`.
- Multiple format specs can be supplied and are printed for each block.

Data flow:
- Reads 32 bytes but normally displays 16 so UTF rune formatting can see bytes beyond the visible block.
- Maintains `nleft` carryover when more than 16 bytes were read.
- Pads short final blocks with zero for formatting.
- Prints a final address line after short read.

Formatters:
- `fmt0`: byte values.
- `fmt1`: big-endian 16-bit words.
- `fmt2`: big-endian 32-bit words.
- `fmt3`: big-endian 64-bit values.
- `fmtc`: ASCII with escapes for tab/CR/LF/backspace and numeric fallback.
- `fmtr`: rune-aware character output with alignment handling for multi-byte runes.
- `swizz`: reverses byte order within each 4-byte word in the 16-byte block.

Input:
- Dumps stdin when no file supplied.
- Dumps one file directly or multiple files with filename titles.

Notable behavior:
- Repeat suppression only runs when `-r` is supplied and compares visible 16-byte blocks.
- 64-bit formatter constructs values from two big-endian 32-bit halves.
