# sources/security-integrity/ecryptfs-utils/src/libecryptfs/cmd_ln_parser.c

## Purpose
Parses eCryptfs mount options and `~/.ecryptfsrc`-style option files into linked lists of `struct ecryptfs_name_val_pair`. It also merges option lists so command-line options can override rc-file defaults while allowing selected duplicate keys.

## Important APIs, types, and functions
- `ecryptfs_parse_options`, `generate_nv_list`, and `process_comma_tok` tokenize comma/newline separated options and `key=module:param=value` forms.
- `parse_options_file`, `ecryptfs_parse_rc_file_fullpath`, and `ecryptfs_parse_rc_file` read option files and the current user's default rc file.
- `ecryptfs_nvp_list_union` merges source pairs into destination pairs with an allowed-duplicates list.
- `copy_nv_pair` and `print_nvp_list` support list manipulation and diagnostics.

## Control flow
Parsing scans a buffer into tokens on comma or newline boundaries. Each token is rejected if empty, too long, or malformed with a leading `=` or `:`. Normal tokens become one linked-list node. Key-module tokens with colon-delimited suboptions recursively create module and parameter nodes. File parsing uses `fstat`, rejects directories and oversized files, reads into a growable buffer for FIFOs or changing input, then invokes the same tokenizer.

## State and persistence behavior
The parser builds heap-allocated linked-list state only; it does not persist data. It reads user configuration from the passwd database and `~/.ecryptfsrc`. Merge operations mutate destination lists in place and may allocate child nodes for parameter trees.

## Dependencies and integration points
Feeds `decision_graph.c` and `module_mgr.c`, where name/value pairs drive noninteractive mount-option selection. It depends on `struct ecryptfs_name_val_pair` and flags from `ecryptfs.h`, and on syslog for diagnostics.

## Risks and edge cases
`MAX_TOK_LEN` constrains individual options to 128 bytes, which can reject long paths or module parameters. Some allocation paths call `memset` immediately after `malloc` before checking the pointer. The colon-list parser is specialized to `key=` and can be fragile for values that legitimately contain commas or colons. Merge logic is acknowledged in comments as a hack around a weak list/tree representation, so duplicate and child handling need careful regression coverage.

## Test signals
High-value tests should cover plain `name=value`, value-less options, repeated `key=` options, colon suboptions, rc-file plus CLI override precedence, allowed duplicate behavior, malformed leading separators, token length boundaries, directory rejection, FIFO reads, and oversized option files.
