# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoerr.c

This module decodes AoE error/config Ethernet-address lists. It has a two-byte header containing command and Ethernet-address count, followed by a list of six-byte addresses.

Filters nominally support command, address count, and address membership. `p_seprint` prints command name and count, then prints up to three Ethernet addresses.

Notable details: the field table maps `ea` to `Onea` rather than `Oea`, so address filters may compile as count filters. The print loop checks and indexes against `m->pe` where `m->ps` appears intended, which can produce incorrect address output. The module is a leaf protocol.
