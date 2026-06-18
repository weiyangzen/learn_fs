# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiOpts.hh

## Purpose

`XrdSecgsiOpts.hh` defines the option mapping tables and parsing helpers used by `XrdSecProtocolgsi.cc` to turn textual GSI configuration values into integer flags. It is included into the implementation file and uses an anonymous namespace, making the option constants and tables internal to each translation unit that includes it.

## Important APIs, types, and constants

- `WARN(x)` writes configuration warnings to `std::cerr`.
- `OTINIT(a,b,x)` initializes an `OptsTab` with option name, default value, number of entries, and mapping array.
- `OptsMap` maps a textual option key to an integer value.
- `OptsTab` stores one option table: option name, default value, mapping count, and `OptsMap *`.
- `LIB_XRDVOMS` defines the default VOMS plugin library name `libXrdVoms.so`.
- `azCallOpts` maps `-authzcall` values: `always` and `novoms`.
- `azPxyOpts` maps `-authzpxy` values for exporting full chain or last cert into `Entity.creds` or `Entity.endorsements`.
- `caVerOpts` maps `-ca` values: `noverify`, `verifyss`, and `verify`.
- `crlOpts` maps `-crl` values: ignore, try, use, use with update, require, and require with update.
- `sDlgOpts` maps server `-dlgpxy` values: ignore or request.
- `gmoOpts` maps `-gmapopt`/GMAP behavior: no map, try map, require map, and DN-name fallback variants.
- `tdnsOpts` maps `-trustdns`/`-showdn` style booleans.
- `vomsatOpts` maps VOMS attribute handling: ignore, extract, require.
- `getOptName(OptsTab &oTab, int opval)` returns the textual name for a mapped value or `"nothing"`.
- `getOptVal(OptsTab &oTab, const char *oVal)` parses either a numeric value or exact textual key and returns the mapped value or the table default with a warning.

## Control flow

Server parameter parsing in `XrdSecProtocolgsiInit` calls `getOptVal` for options such as `-crl`, `-gmapopt`, `-authzcall`, `-dlgpxy`, `-authzpxy`, `-vomsat`, `-trustdns`, and `-showdn`. `gsiOptions::Print` calls `getOptName` to render the current settings for trace output. `XrdSecProtocolgsi::Init` also uses constants such as `caVerifyss`, `crlTry`, `dlgReqSign`, `gmoTryMap`, `vatIgnore`, and authz proxy constants to interpret the integer options.

The parser first treats strings beginning with a digit as numeric and accepts them only when equal to a mapped value. Non-numeric strings must match a mapping key exactly. Invalid values fall back to `opDflt` when that default is nonnegative and print a warning.

## State and persistence behavior

The file defines internal static constants and non-const mapping arrays/tables. There is no runtime persistence or dynamic allocation. Because the content is in an anonymous namespace in a header, every translation unit including the header gets its own internal copies. In this repository scope it is included by the main protocol implementation.

## Dependencies and integration points

This header expects standard C/C++ functions and streams used by `isdigit`, `atoi`, `strcmp`, and `std::cerr`; the including translation unit provides the relevant includes. Its constants are consumed directly by `XrdSecProtocolgsi.cc` and defaults in `XrdSecProtocolgsi.hh`'s `gsiOptions` constructor. It also defines `LIB_XRDVOMS`, used when server config says `-vomsat` without an explicit VOMS plugin.

## Risks and edge cases

- `getOptVal` dereferences `*oVal` without null or empty checks. Current callers pass substrings after recognized `-opt:` prefixes, but malformed empty values can still reach it.
- Numeric parsing accepts only values present in the mapping table. This is good for validation but means composite future values must be added to the table.
- Invalid values silently become defaults after warning. For security options such as `-ca`, `-crl`, `-gmapopt`, and `-trustdns`, fallback defaults must be reviewed to avoid surprising permissive behavior.
- The currently disabled two-table `getOptVal` overload suggests older support for comma-composed values; adding new combined options requires care.
- In the observed server parser, `-ca:` calls `getOptVal(caVerOpts, op+4)` and then immediately overwrites the result with `atoi(op+4)`, which undermines this header's symbolic parser for `-ca`. That issue is in the consumer but directly affects these tables.

## Test signals

Unit tests should cover every option table with textual values, numeric values, and invalid strings. Security-focused tests should assert defaults for invalid `-ca`, `-crl`, `-gmapopt`, `-vomsat`, `-dlgpxy`, `-authzpxy`, and `-trustdns`. Integration tests should parse realistic server parameter strings and verify that `gsiOptions` receives the expected integers, especially `-ca:verifyss` and `-ca:verify`.
