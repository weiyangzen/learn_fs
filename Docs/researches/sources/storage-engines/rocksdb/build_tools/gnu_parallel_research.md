# sources/storage-engines/rocksdb/build_tools/gnu_parallel

## Purpose
This file is a vendored Perl copy of GNU Parallel 20141122, with RocksDB-specific behavior in its progress loop: when CI-style progress output has not advanced for about five minutes, it runs `build_tools/ps_with_stack` from the script directory, falling back to `ps -wwf`. RocksDB uses it from the top-level `Makefile` to run generated test commands in parallel with `--joblog=LOG`, `--eta`, `--plain`, and `--tmpdir=$(TEST_TMPDIR)`. Keeping the tool vendored makes parallel test scheduling available even when GNU Parallel is not installed system-wide, while letting RocksDB modify hang diagnostics.

## Important APIs, types, and functions
The script is executable Perl and uses `IPC::Open3`, `POSIX`, `Symbol`, `File::Temp`, `File::Path`, `Getopt::Long`, and `File::Basename`. It is organized as top-level orchestration plus several package-style classes.

`parse_options`, `options_hash`, `read_options`, `read_args_from_command_line`, `open_joblog`, `parse_env_var`, and `find_compression_program` establish global option state in `opt::` and `Global::`. They support normal GNU Parallel features such as `-j/--jobs`, `--joblog`, `--resume`, `--results`, `--pipe`, `--pipepart`, `--sshlogin`, `--return`, `--transfer`, `--halt`, `--timeout`, `--eta`, `--bar`, `--colsep`, xargs compatibility flags, semaphore mode, profiles, and `$PARALLEL`.

`JobQueue`, `CommandLineQueue`, `CommandLine`, `RecordQueue`, `RecordColQueue`, `MultifileQueue`, and `Arg` form the input and command construction pipeline. `CommandLineQueue->new` rewrites replacement strings such as `{}`, `{#}`, `{%}`, `{/}`, `{/.}`, positional variants, and `{= perl code =}` into internal markers. `CommandLine->populate`, `len`, `replace_placeholders`, and `Arg->replace` decide how many records fit under command-line length limits and produce the final shell command.

`SSHLogin` models each local or remote execution target. It tracks job counts, CPU/core discovery, load and swap probes, host groups, SSH command parsing, ControlMaster path setup, rsync transfer commands, remote cleanup commands, and per-host process limits. `remote_hosts`, `read_sshloginfiles`, `parse_sshlogin`, `filter_hosts`, `setup_basefile`, and `cleanup_basefile` integrate that model with command-line options.

`Job` models one running command. Important methods include `wrapped`, `sshlogin_wrap`, `openoutputfiles`, `start`, `print`, `linebuffer_print`, `print_joblog`, `should_be_retried`, `kill`, `family_pids`, `transfer`, `sshtransfer`, `return`, `sshreturn`, `sshcleanup`, and `workdir`. It owns stdout/stderr temp files or result files, process IDs, sequence number, slot number, exit status, timeout state, retry state, transfer sizes, and remote wrapping.

`init_run_jobs`, `start_more_jobs`, `start_another_job`, `drain_job_queue`, `progress`, `compute_eta`, `reaper`, `process_failed_job`, and `print_earlier_jobs` implement scheduling, progress display, failure accounting, and output ordering. This is also where RocksDB's hang diagnostic hook calls `ps_with_stack`.

`pipe_part_files`, `find_header`, `find_split_positions`, `cat_partial`, `spreadstdin`, `write_record_to_pipe`, and related helpers implement `--pipe` and `--pipepart` by splitting stdin or files on record boundaries and feeding chunks to jobs.

`Semaphore` implements GNU Parallel's semaphore mode using link-count-based locks in `~/.parallel/semaphores/id-<name>`.

## Control flow
At startup the script saves original stdin/stdout/stderr and inherited file descriptors, installs signal handlers, parses options and profiles, determines how many input records each command should consume, and opens input sources from `-a`, `::::`, or stdin. Header processing can rewrite command placeholders from column names to positional placeholders.

If `--filter-hosts` is active, remote hosts are tested with nested `parallel` invocations that query remote CPU/core counts, maximum command length, and login latency. `--onall` and `--nonall` take an alternate path that spawns one sub-parallel per host and exits after all host runs complete.

The normal path constructs `Global::JobQueue`, optionally pre-counts jobs for `--eta` or `--bar`, prepares `--pipepart` cat commands, asks each `SSHLogin` for its maximum runnable job count, optionally acquires a semaphore, and starts jobs. `start_more_jobs` walks hosts round-robin and starts a job only when host slots, load, swap, SSH delay, process limits, and file descriptor checks permit it. `start_another_job` pulls a `Job` from the queue, skips already-completed commands for `--resume`/`--results`, binds the host, and calls `Job->start`.

`Job->start` prepares grouped, ungrouped, result-directory, compressed, or file-output handles, sets `PARALLEL_SEQ` and `PARALLEL_PID`, and launches the wrapped command through the selected shell using `open3`. For remote hosts, `Job->wrapped` layers quoting, `nice`, `--cat`/`--fifo`, SSH, file transfer, return-file retrieval, cleanup, `--pipe` EOF detection, and optional tmux wrapping in a strict order.

`drain_job_queue` loops until no jobs are running and the queue is empty or no-new-jobs has been requested. It periodically calls `reaper`, starts more jobs when slots free up, prints ETA/progress, and in non-terminal CI mode emits progress every 30 seconds only when progress is advancing. If progress does not advance for around 300 seconds, it runs `ps_with_stack` to dump process and stack state for relative-path test binaries.

`reaper` handles child exits, updates exit status and runtime, releases slots, updates timeout statistics, prints output or buffers it for `--keep-order`, logs job rows, applies retry logic, and decrements host counts. Final cleanup removes base files, releases semaphores, terminates SSH master processes, and exits with either the bounded global failure count or a halt-on-error status.

## State and persistence behavior
Most runtime state is in global package variables, including `Global::running`, `Global::host`, `Global::total_running`, `Global::total_started`, `Global::JobQueue`, `Global::exitstatus`, `Global::job_already_run`, and replacement maps. Jobs also store state in per-object hashes.

Persistent and semi-persistent files are important. `--joblog` writes tab-separated rows with sequence, host, start time, runtime, bytes sent/received, exit value, signal, and command; `--resume` and `--resume-failed` read this file back to skip completed work. `--results` creates a directory tree derived from input arguments and writes `stdout`/`stderr` files. Profile and environment behavior reads `/etc/parallel/config`, `~/.parallel/config`, `~/.parallelrc`, `~/.parallel/<profile>`, `$PARALLEL`, and `~/.parallel/ignored_vars`.

The script writes temp files under `$TMPDIR` with names like `parXXXXX` for grouped output, arg files, host checks, and disk-full probes. It also uses `~/.parallel/tmp` for command-line length caches, load-average probes, swap probes, ControlMaster directories, and dynamic workdirs, and `~/.parallel/will-cite` to suppress citation notices. Semaphore mode persists lock directories and process-id files under `~/.parallel/semaphores`.

## Dependencies and integration points
RocksDB's `Makefile` invokes this script for `make check` and related parallel test paths, and comments there explicitly depend on this tool handing jobs out in input order. `Makefile` also notes that `--eta` is always used and this vendored copy has been modified for useful output on non-terminal CI systems. The script invokes `build_tools/ps_with_stack` by deriving the sibling script path from `dirname($0)`.

External tools used at runtime can include `ssh`, `rsync`, `tmux`, `ps`, `vmstat`, `sysctl`, `nproc`, `resize`, shell utilities, compression programs such as `lzop` or `gzip`, `gdb`/`pstack` indirectly through `ps_with_stack`, and remote `parallel` when querying remote hosts. Perl modules beyond core/standard modules are optional for debugging (`Time::HiRes`, `Text::ParseWords`, `Data::Dump`, `Data::Dumper`, `Devel::Size`, `Carp`, `Cwd`, `Fcntl`, `IO::Poll` in a remote wrapper string).

## Risks and edge cases
The script executes constructed shell strings and also evaluates replacement Perl expressions from user-provided `{= ... =}` placeholders. That is GNU Parallel behavior, but it means untrusted commands, arguments, profiles, `PARALLEL`, or replacement expressions must not be accepted in privileged contexts.

The file is an old vendored GNU Parallel snapshot. It has portability code for many operating systems, but modern environments may expose behavior changes in Perl, OpenSSH, rsync, shells, process listings, or CI signal handling. The script writes to `$HOME/.parallel`; missing, shared, or permission-constrained home directories can affect caches, citation notices, load probes, and semaphores. `HOME` is forced to `/tmp` when absent, which can create shared state across users or jobs.

Resource probing intentionally forks children and opens many file handles to estimate limits. On constrained CI hosts this can emit warnings, reduce concurrency, or fail before running tests. Grouped output and `--eta` pre-counting can read large input streams and write temporary files; full `$TMPDIR` is detected with `exit_if_disk_full`, but a disk-full event can still make test output incomplete.

Remote execution and transfer paths rely heavily on shell quoting, rsync semantics, login shell detection, ControlMaster cleanup, and remote GNU Parallel availability. Pathnames with unusual characters are quoted, but remote commands and user profiles remain high-risk surfaces. `--timeout` percentage mode depends on observed runtimes and can terminate slow tests if the remedian-derived threshold is too low.

The RocksDB-specific `ps_with_stack` hook runs only after progress has stopped in non-terminal output. It is diagnostic, not a scheduler fix; if `pstack` or `gdb` is unavailable or blocked by ptrace restrictions, the fallback is basic `ps`.

## Test signals
Primary test signal is indirect: RocksDB's `make check`, parallel test targets, and valgrind test paths exercise this script with `--joblog`, `--eta`, and `--tmpdir`. Successful runs should produce a valid `LOG`, per-test logs under `t/`, preserved or intentionally grouped output, and a zero exit code when all test commands pass.

Useful focused checks include `build_tools/gnu_parallel --gnu --help`, `build_tools/gnu_parallel --version`, a small local run such as `printf 'a\nb\n' | build_tools/gnu_parallel -j2 --plain echo {}`, a `--joblog`/`--resume` run, a `--keep-order` run, and a `--pipe` run against record-separated input. For the RocksDB modification, a CI-style non-terminal parallel run with a deliberately hung relative-path command should eventually print process information and attempt stack dumps through `ps_with_stack`.
