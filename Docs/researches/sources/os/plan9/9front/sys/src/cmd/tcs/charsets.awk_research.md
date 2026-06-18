# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.awk

Generates charset alias entries from IANA charset XML and a local `tcs.txt`-style mapping file.

Key points:
- Intended input is `character-sets.xml` plus a second mapping file supplied as `ARGV[2]`.
- On `<name>` blocks, normalizes the charset name to lowercase, records it as canonical, and starts an alias list.
- On `<alias>` blocks, normalizes aliases to lowercase and adds them to the current canonical name.
- In `END`, reads the second file; for each `tcs` charset name found in the parsed IANA names, prints `"alias", "converter",` entries for every alias associated with that canonical name.
- Uses simple XML tag stripping with `gsub(/[<>\/]+/, " ")`.

Dependencies and interactions:
- Used as a build/generation helper for `tcs` charset alias tables.
- Assumes a simple IANA XML structure where name/alias text is in `$2` after tag stripping.

Research relevance:
- Build-time script that keeps `tcs` charset aliases aligned with IANA names and local converter names.
