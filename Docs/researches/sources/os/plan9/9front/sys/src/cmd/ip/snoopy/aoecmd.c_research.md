# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoecmd.c

This module decodes AoE configuration command payloads. The payload includes buffer count, firmware version, sector count, command/version nibble, length, and configuration string bytes.

It supports a single `cmd` filter that compares the low nibble of `ccmd`. `p_seprint` prints buffer count, firmware, sector count, version, command, length, and then renders the following config string with the declared length.

This is a leaf AoE sub-protocol with no further demux.
