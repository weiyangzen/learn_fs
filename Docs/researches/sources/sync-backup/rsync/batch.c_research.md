# sources/sync-backup/rsync/batch.c

Purpose: supports `--write-batch`, `--only-write-batch`, and `--read-batch` stream replay.

Important APIs/types/functions: globals `batch_fd`, `batch_sh_fd`, `batch_stream_flags`; public `write_stream_flags()`, `read_stream_flags()`, `check_batch_flags()`, `open_batch_files()`, and `write_batch_shell_file()`; helpers `write_arg()`, `write_opt()`, and `write_filter_rules()`.

Control flow: writer records a bitmap of stream-affecting options. Reader checks and adjusts local flags to match the batch, with special handling for protocol versions and iconv. Batch-file open creates data and shell wrapper files. Shell script generation quotes arguments, converts write-batch option to read-batch, elides source/destination args, and appends filter rules via heredoc.

State and persistence: creates batch data file and executable `.sh` wrapper; mutates global options to match batch stream flags.

Dependencies/integration: depends on option globals, protocol version, filter lists, shell quoting, file IO, and cleanup error exits.

Risks: generated shell command uses heuristics and does not understand all options. Stream flag mismatch can silently mutate options except iconv, which is fatal.

Test signals: batch-related suite tests and protocol CI runs cover replay compatibility.
