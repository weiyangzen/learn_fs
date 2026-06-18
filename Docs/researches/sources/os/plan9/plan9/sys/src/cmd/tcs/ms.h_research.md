# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ms.h

## Purpose

`ms.h` defines Microsoft/IBM/OEM/Windows 256-entry code page tables for Plan 9 `tcs`.

## Contents

The file begins with a commented Plan 9 `rc` script showing how tables were generated from Microsoft GlobalDev reference pages. It then defines these arrays:

- `tabcp437`
- `tabcp720`
- `tabcp737`
- `tabcp775`
- `tabcp850`
- `tabcp852`
- `tabcp855`
- `tabcp857`
- `tabcp858`
- `tabcp862`
- `tabcp866`
- `tabcp874`
- `tabcp1250`
- `tabcp1251`
- `tabcp1252`
- `tabcp1253`
- `tabcp1254`
- `tabcp1255`
- `tabcp1256`
- `tabcp1257`
- `tabcp1258`

Each maps byte values `0x00..0xff` to Unicode rune values, with `-1` where the code page leaves a byte undefined.

## Integration

`tcs.c` includes `ms.h` directly and registers these tables under `ibm*`, `windows-*`, and compatibility aliases:

- `ibm437`, `msdos` -> `tabcp437`
- `ibm720`, `ibm737`, `ibm775`, `ibm850`, `ibm852`, `ibm855`, `ibm857`, `ibm858`, `ibm862`, `ibm866`, `ibm874`
- `windows-1250` through `windows-1258`
- `microsoft` -> `tabcp1252`
- `ps2` -> `tabcp850`

The arrays are used via generic table conversion in `tcs.c`.

## Notes

Like `misc.h`, this is a storage-defining header. It should not be included in multiple C files unless the build intentionally wants duplicate definitions, which standard C linkers generally reject. The active registry in `tcs.c` is the source of which arrays are reachable by command-line charset names.
