# sources/test-tools/ltp/testcases/kernel/fs/doio/iogen.c

Purpose: random I/O request generator for the legacy LTP `doio` stress pipeline. It parses command-line ranges, creates or sizes target files, chooses syscall/open-flag/offset combinations, and emits binary `struct io_req` records with `DOIO_MAGIC` to stdout or a FIFO.

Important APIs/types/functions: `main`, `parse_cmdline`, `form_iorequest`, `get_file_info`, `create_file`, `init_output`, `startup_info`, `str_lookup`, `value_to_string`, `struct file_info`, `struct strmap`, `Syscall_Map`, `Flag_Map`, and `Omode_Map`. It integrates helpers from `doio.h`, `random_range.h`, `open_flags.h`, `string_to_tokens.h`, and byte-size parsing.

Control flow: startup clears umask, probes platform support, parses options, opens stdout/FIFO output, seeds `random_range`, prints configuration unless quiet, then loops by count, time, or forever. Each iteration chooses a syscall, file, open flag profile, transfer size, offset mode (`sequential`, `reverse`, `random`), optional overlap, and async completion strategy before writing one packed request structure.

State/persistence behavior: persistent state includes files created or resized from `[len:]file` arguments and FIFO output created by `-p`. In-memory state tracks per-file last offset/length so sequential, reverse, random, and overlap modes can generate related requests. On SGI/Cray paths it can request raw, realtime, reserve, or allocate behavior; Linux defaults to buffered and sync I/O with 512-byte raw alignment.

Dependencies/integration: intended to be piped into `${{LTPROOT}}/testcases/bin/doio`, and commonly launched by `rwtest`. It depends on platform `open(2)`, `stat(2)`, `fcntl(2)`, `lseek(2)`, `write(2)`, filesystem semantics, and the binary layout in `doio.h`.

Risks/test signals: binary protocol changes must stay synchronized with `doio`. Alignment and file-size validation are critical; too-small files are ignored, and all files being rejected is a fatal condition. Some platform options are disabled on Linux. Success is a stream of valid request records; failures are stderr diagnostics, nonzero exits, or downstream `doio` errors.
