# sources/user-network-fs/samba/source3/printing/load.c

## Purpose
`load.c` loads printer services from Samba's pre-populated printer capability/cache data into loadparm service entries. It bridges the printer list cache and `[printers]` share configuration so automatic printer shares become available.

## Important APIs, types, and functions
- `load_printers()` is the public entry point. It checks the pcap/printer cache, loads configured printer services, and adds cached printers.
- `pcap_cache_loaded(time_t *_last_change)` reports whether the printer cache has a last-refresh timestamp and optionally returns it.
- `add_auto_printers()` handles the `auto services` list by adding named printers that exist in the printer list and are not already configured as services.

## Control flow
`load_printers` first refuses work if `pcap_cache_loaded(NULL)` fails. It then calls `add_auto_printers`, calls `lp_load_printers`, checks that a `[printers]` service exists, and finally iterates cached printer names with `printer_list_read_run_fn(lp_add_one_printer, NULL)`. `add_auto_printers` ensures `[printers]` exists, including a registry-service fallback, copies the configured auto-service string, tokenizes it by Samba list separators, skips already configured services, and adds entries only for names present in the printer list.

## State and persistence behavior
The file does not persist printer data directly. It mutates in-memory loadparm service state by calling `lp_add_printer` and `lp_add_one_printer`. The cache freshness signal comes from `printer_list_get_last_refresh`, which is maintained by the printer list subsystem.

## Dependencies and integration points
It depends on `printing/pcap.h`, `printing/printer_list.h`, `printing/load.h`, and loadparm. It integrates with registry service processing, `lp_load_printers`, and consumers that need print shares loaded before serving SMB/RPC printer operations.

## Risks and edge cases
- If the pcap/printer cache has not been refreshed, no printers are loaded.
- Without `[printers]`, automatic pcap additions are intentionally skipped.
- Auto-services are tokenized with `strtok_r` on a duplicated string; unusual separator or printer-name characters can affect parsing.
- Failures in `printer_list_read_run_fn` are logged but do not abort the process.

## Test signals
Tests should seed a printer list cache, configure `[printers]` and `auto services`, call `load_printers`, and assert expected loadparm services appear. Negative tests should cover missing pcap refresh, missing `[printers]`, and pre-existing service names.
