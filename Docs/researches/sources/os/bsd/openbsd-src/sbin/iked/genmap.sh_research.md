# File Research: sources/os/bsd/openbsd-src/sbin/iked/genmap.sh

`genmap.sh` is a build helper that generates `struct iked_constmap` arrays from header definitions. It takes an input header and token name, derives map names from existing `struct iked_constmap` declarations, then emits C source with license/header includes and generated map entries.

The script uppercases/lowercases the token, scans `#define` lines with comments, and turns constants of the form `${TOKEN}_${MAP}_... /* description */` into `{ value, "name", "description" }` entries.

It is simple shell/sed/grep generation logic and assumes comments/defines follow the expected formatting. It does not participate at runtime.
