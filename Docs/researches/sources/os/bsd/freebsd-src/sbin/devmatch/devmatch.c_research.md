# File Research: sources/os/bsd/freebsd-src/sbin/devmatch/devmatch.c

## Purpose
Matches unattached or NOMATCH devices against kernel module linker hints and prints modules that may bind them.

## Main Elements
- Options: all, dump, hints path, nomatch string, quiet, unbound, verbose.
- `read_linker_hints()`: reads explicit or `kern.module_path` linker.hints files, validates versions, and merges multiple hint files.
- Hint readers: `getint()` and `getstr()` decode aligned linker-hints records.
- `pnpval_as_int()` / `pnpval_as_str()`: extract PNP key values from event/device PNP info strings.
- `search_hints()`: walks module/PNP hint records, applies numeric/string/mask/key matching rules, prints matching modules, dumps hints, or reports unbound devices.
- `find_unmatched()`: walks the devinfo tree for enabled, unattached/unbound devices and searches hints.
- `find_nomatch()`: parses a NOMATCH event string, filters devices already attached once, and searches hints for that event.
- `main()`: reads hints, optionally dumps, initializes devinfo, and searches either NOMATCH or all devices.

## Dependencies And Integration
Used by `devd/devmatch.conf` through `service devmatch quietstart $*`. Reads kernel module hints and the live device tree.

## Risk Notes
PNP string parsing is specialized and contains comments about imperfect key override handling and simple quoted copying. Matching quality depends on linker.hints metadata format and device event strings.
