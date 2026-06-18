# File Research: sources/virtualization/nbdkit/plugins/data/format.h

Public internal header for the data plugin format parser.

Key contents:
- Includes allocator API.
- Declares `read_data_format(const char *value, struct allocator *a, uint64_t *size)`, which parses the `data=` mini-language and materializes it into an allocator.
