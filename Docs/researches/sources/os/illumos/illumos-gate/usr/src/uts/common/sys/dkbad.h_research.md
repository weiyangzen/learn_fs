# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkbad.h

This legacy disk header defines structures for DEC STD 144-style bad sector forwarding. It has no includes.

The comments describe bad-sector information stored in the first five even-numbered sectors of the last track of the disk pack, with up to 126 bad sectors supported. The alternate sectors are located in the last track of the `c` filesystem partition.

`NDKBAD` is 126. `struct dkbad` stores cartridge serial number, bad-sector table size, and an array of bad track/sector entries. Nested `struct bt_bad` stores cylinder, track, and sector.

Research notes:
- This is legacy disk metadata support retained for compatibility.
- The structure layout is disk-format/user-visible for old tools or drivers.
