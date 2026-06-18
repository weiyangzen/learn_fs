# File Research: sources/virtualization/nbdkit/filters/partition/Makefile.am

This build fragment compiles the partition filter from `partition.c`, `partition.h`, `partition-gpt.c`, and `partition-mbr.c`. It includes `common/gpt`, core includes, and `common/utils`, and links utility/replacement libraries plus the platform import library.

It distributes `nbdkit-partition-filter.pod` and conditionally builds the man page. Build dependencies reflect that the implementation parses both MBR and GPT partition tables and uses shared endian/GPT structures.
