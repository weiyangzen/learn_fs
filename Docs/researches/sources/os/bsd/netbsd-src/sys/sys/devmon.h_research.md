# File Research: sources/os/bsd/netbsd-src/sys/sys/devmon.h

Declares the device monitor event insertion interface.

Key content:
- Includes `<prop/proplib.h>`.
- `int devmon_insert(const char *, prop_dictionary_t);`

Important behavior:
- Small bridge for reporting device events with proplib dictionaries.
- Header guard begins after the proplib include.
