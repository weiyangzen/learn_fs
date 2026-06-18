# sources/storage-engines/rocksdb/build_tools/ps_with_stack

## Purpose
This Perl utility prints a wide process tree and attempts to dump stack traces for processes that look like locally built test binaries. It is designed as a diagnostic companion for `build_tools/gnu_parallel`: when parallel test progress stalls in CI, `gnu_parallel` runs this script to reveal which relative-path commands are still running and what their thread stacks look like.

## Important APIs, types, and functions
The script is small and procedural. It uses `strict`, opens `ps -wwf` as a read pipe, parses the header row to discover the `PID` and `CMD` column indexes, and then inspects each subsequent row. For matching rows, it invokes `system("pstack $pid || gdb -batch -p $pid -ex 'thread apply all bt'")`.

## Control flow
The script starts `ps -wwf`, initializes `$cols_known`, `$cmd_col`, and `$pid_col`, and loops over every output line. It prints each `ps` line immediately. Until it sees a line containing `CMD`, it treats that line as the header and records the positions of `PID` and `CMD`.

After the header is known, each row is split on whitespace. The script extracts the PID and command by the recorded indexes. It only dumps stacks when the PID is numeric and the command looks like a relative path containing a slash but not starting with slash, using the pattern `^[^/ ]+[/]`. This matches commands such as `./my_test` or `foo/bar_test`, while avoiding `/usr/bin/time`, `grep`, and other commands found through absolute paths or `$PATH`.

## State and persistence behavior
The script has no persistent state and writes only to stdout/stderr inherited from its caller. It does not create files. Its only side effects are attaching to matching processes through `pstack` or `gdb`, which may temporarily stop or inspect processes depending on platform/tool behavior.

## Dependencies and integration points
It depends on Perl, `ps`, and either `pstack` or `gdb`. It is invoked by the vendored `gnu_parallel` script using `$script_dir/ps_with_stack || ps -wwf`, so if it fails, RocksDB still receives a process listing. It is intended for Linux-like development or CI hosts where built RocksDB tests are executed by relative path.

## Risks and edge cases
Parsing `ps` output by whitespace is inherently format-sensitive. Commands with whitespace before the first command word, unusual `ps` implementations, or headers that do not use `CMD`/`PID` as expected may lead to missed or incorrect matches. Because only the first whitespace-delimited command field is used, arguments do not affect matching.

`gdb -batch -p` and `pstack` can fail due to missing tools, ptrace restrictions, container security settings, different users, or hardened kernels. The command string interpolates only a numeric PID after validation, so shell injection risk is low. However, stack dumping every matching relative-path process can be expensive during large test runs.

## Test signals
A basic check is running `build_tools/ps_with_stack` during an active RocksDB test run and confirming it prints the `ps -wwf` listing plus "Dumping stacks for <pid>..." for relative-path test binaries. In restricted CI, an acceptable signal is that it still prints process lines even if `pstack` and `gdb` fail. Its integration signal is visible diagnostic output from stalled `make check` runs that use `gnu_parallel --eta`.
