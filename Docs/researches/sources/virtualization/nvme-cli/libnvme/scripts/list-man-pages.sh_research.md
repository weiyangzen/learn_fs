# File Research: sources/virtualization/nvme-cli/libnvme/scripts/list-man-pages.sh

This Bash helper extracts documented symbol names from a source file.

Core behavior:
- Reads the file passed as `$1`.
- Uses sed patterns to find kernel-doc comments for functions, structs, and enums.
- Prints each matched symbol name.

Integration role:
- Likely used by documentation tooling to enumerate generated man page targets.
