# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/iana_ports.inc

Generated numeric include file containing IANA-assigned port numbers.

Key contents:
- 5,507 sorted integer entries.
- Minimum value: `1`.
- Maximum value: `49001`.
- Entries are strictly increasing; no duplicate or non-increasing entry was found.
- Format is a comma-terminated integer per line, intended to be included inside a C initializer.

Use in tree:
- Included by `util/config_file.c` inside `init_outgoing_availports()`:
  - initializes outgoing available ports from `1024` upward;
  - clears `49152..49407` to leave a slice of ephemeral ports available to other programs;
  - clears every port listed by `iana_ports.inc` so Unbound avoids IANA-assigned ports for outgoing random-port selection.

Research notes:
- The file contains data only, no declarations, comments, or code.
- Comment at inclusion site says it is generated with `make iana_update`.
- Because the include is embedded in a C array with an added `-1` sentinel after it, each line intentionally has a trailing comma.
