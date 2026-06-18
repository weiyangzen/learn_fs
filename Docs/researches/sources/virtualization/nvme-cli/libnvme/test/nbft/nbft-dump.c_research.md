# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump.c

## Role

`nbft-dump.c` is a deterministic dumper for parsed NBFT data. It is used by the NBFT golden-output tests.

## Behavior

`main()` creates a libnvme context, parses the NBFT table file path supplied on the command line with `libnvmf_read_nbft()`, prints a structured text representation, frees the parsed table, and exits nonzero on usage or parse errors.

`print_nbft()` prints raw table size, host UUID/NQN/configuration flags, primary flag, HFI entries, TCP properties, security entries, discovery entries, and subsystem namespace entries. It follows object relationships by printing referenced HFI, security, and discovery indexes.

`print_hex()` prints raw byte arrays such as UUIDs, MAC addresses, and namespace identifiers without separators.

## Dependencies

- Public libnvme API and NBFT structures.
- Standard C stdio/stdlib/string/unistd.

## Filesystem/Storage Relevance

The file validates libnvme’s parsing of NVMe-oF boot configuration exposed through ACPI NBFT tables.
