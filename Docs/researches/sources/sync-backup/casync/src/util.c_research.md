# sources/sync-backup/casync/src/util.c

Purpose: implements broad low-level utilities for I/O, sparse writes, randomness, path/string handling, numeric parsing, fd/directory helpers, temporary directory selection, process waiting, and bounded line reading.

Important APIs/types/functions: key functions include `loop_write`, `loop_write_block`, `loop_read`, `write_zeroes`, `loop_write_with_holes`, `skip_bytes`, `dev_urandom`, hex helpers, `filename_is_valid`, `tempfn_random`, `hexdump`, `dirname_malloc`, `strjoin_real`, `ls_format_*`, `safe_atoi/atou/atollu/atollx`, `readlink*_malloc`, string-vector helpers, `xopendirat`, `progress`, `strextend`, `parse_uid`, `wait_for_terminate`, `page_size`, boolean parsing, `greedy_realloc*`, `skip_bytes_fd`, `rename_noreplace`, `path_startswith`, tmp dir lookup, `path_is_safe`, `is_dir`, `free_and_strdup`, `read_line`, `delete_trailing_chars`, and `strstrip`.

Control flow/state: most helpers are stateless. `dev_urandom` caches getrandom availability, `page_size` caches sysconf, and `progress` tracks spinner position/time. Sparse writing scans zero runs of at least 4096 bytes and uses hole punching when possible.

Dependencies/integration: central dependency for nearly every casync module and test. It wraps Linux features such as fallocate, renameat2, getrandom, statfs, and file attributes while preserving negative-errno style.

Risks/test signals: high blast radius; edge cases include short writes, nonblocking fds, sparse-file fallbacks, integer overflow, unsafe paths, and non-atomic `rename_noreplace` fallback. `test-util.c` directly verifies sparse write/read behavior; many other tests exercise paths indirectly.

Source research group: `subset-b-009122`.
