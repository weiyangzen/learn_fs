# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/sff.c

## Purpose
`sff.c` implements non-`SMALL` transceiver EEPROM/DDM reporting for OpenBSD `ifconfig`. It reads SFF/QSFP/XFP pages via `SIOCGIFSFFPAGE`, decodes module identity, connector/media distances, vendor strings, serial/date fields, voltage, temperature, optical power, bias current, thresholds, warnings, and optional raw hex dumps. `ifconfig.c` calls `if_sff_info(0)` for `transceiver`/`sff` status and `if_sff_info(1)` for `sffdump`.

## Standards and Module Types
The file contains constants and register offsets for:
- SFF-8024 identifiers/connectors;
- SFF-8472 SFP/GBIC EEPROM and DDM page `0xa2`;
- SFF-8436/SFF-8636 QSFP/QSFP+/QSFP28 lower and upper pages;
- INF-8077 XFP page layout.

It maps known transceiver identifiers and connector types to readable names and falls back to `Reserved` or `Vendor Specific`.

## Data Structures
- `struct sff_thresholds` stores high alarm, low alarm, high warning, and low warning thresholds.
- `struct sff_media_map` abstracts media-printing offsets/scales for connector, wavelength, SMF/OM distances, and copper distance across SFF-8472 and upper-page layouts.
- `sff8472_media_map` and `upper_media_map` configure those offsets.

## Page Access Flow
- `if_sffpage_init()` fills `struct if_sffpage` with `ifname`, I2C address, and page.
- `if_sff_info()` reads EEPROM page 0. If page 0 fails with `ENXIO`, it tries page 1 for XFP devices that cannot switch pages.
- Optional `dump` mode prints page address/page number and calls `hexdump()`.
- It inspects byte 0 for SFF-8024 identifier, prints the transceiver type, and dispatches:
  - SFP/GBIC -> `if_sff8472()`;
  - XFP -> `if_inf8077()`, ensuring page 1 is loaded;
  - QSFP/QSFP+/QSFP28 -> `if_sff8636()`;
  - unknown types -> type line only.

## String and Numeric Decoding
- `if_sff_ascii_print()` trims whitespace/NULs from fixed-width fields and uses `vis()` to safely print control characters.
- `if_sff_date_print()` formats six-digit `YYMMDD` as `20YY-MM-DD`, falling back to raw ASCII if non-digits appear.
- `if_sff_int()` and `if_sff_uint()` decode big-endian 16-bit signed/unsigned values.
- `if_sff_power2dbm()` converts 0.1 uW style power fields to dBm using `log10f()`.
- `if_sff_printalarm()` prints actual readings and optional threshold ranges, marking `[ALARM]` or `[WARNING]`.

## Media and Distance Output
`if_sff_printmedia()` prints connector name, wavelength when meaningful, and distances:
- SFF-8472 uses separate SMF meters/km fields and OM1/OM2/OM3 scale factors.
- Upper-page formats use a shared map with wavelength factor 20.0 and OM/copper offsets.
- Zero values are omitted; large distances are formatted in kilometers.

## SFF-8472 SFP/GBIC Path
`if_sff8472()` prints media, vendor/product/revision, serial, and date. It checks compliance and DDM-implemented bits before reading DDM page `IFSFF_ADDR_DDM`. It prints external-calibration warning if needed, then displays:
- voltage;
- TX bias current;
- temperature;
- TX optical power;
- RX optical power.
Each metric is compared to alarm/warning thresholds.

## XFP Path
`if_inf8077()` currently calls `if_upper_strings()` only, so it reports media plus vendor/product/revision/serial/date/lot fields, without DDM metrics.

## QSFP Path
`if_sff8636()` prints upper-page strings, checks `Data_Not_Ready`, max case temperature, and base temperature/voltage/channel fields. If paged memory is available, `if_sff8636_thresh()` reads page 3, validates page select, decodes alarm/warning thresholds, and prints threshold-aware:
- module temperature;
- voltage;
- per-channel TX bias;
- per-channel TX power;
- per-channel RX power.
If threshold page is not available or readings look unset, dump mode still prints fallback raw/current values.

## Hex Dump Support
`hexdump()` prints 16 bytes per line with hex bytes plus printable ASCII. `printable()` maps NUL to `_` and non-printable bytes to `~`.

## Error Handling and Risks
The file returns `-1` for page read failures so callers can decide whether to warn or fail. Most formatting assumes EEPROM data has standard-sized fields but guards output with fixed buffer lengths. Risk areas include unsupported external calibration, potentially `log10f(0)` on zero optical-power fields, and specification drift for newer SFF-8024 module identifiers not present in the static name tables.
