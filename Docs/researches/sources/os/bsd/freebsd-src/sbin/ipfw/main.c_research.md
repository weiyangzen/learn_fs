# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/main.c

## Purpose

`main.c` is the command-line entry point for the `ipfw` and `dnctl` binaries. It provides top-level usage text, normalizes command-line arguments, sets global options in `g_co`, dispatches commands to the handler functions declared in `ipfw2.h`, and supports reading command files with optional preprocessing.

The file distinguishes behavior by executable basename: `dnctl` restricts the command set to dummynet operations, while any other basename acts as `ipfw`.

## Main Flow

`main()`:

1. Performs Windows/TCC Winsock setup when compiled in that environment.
2. Sets `g_co.prog` based on `basename(av[0])`.
3. If the last argument is an absolute readable pathname, treats it as a command file and calls `ipfw_readfile()`.
4. Otherwise calls `ipfw_main()`.
5. On parser failure, exits with usage guidance.

`help()` prints separate syntax summaries for `ipfw` and `dnctl`, then exits.

## Argument Normalization

`ipfw_main()` receives an argument vector including program name. It supports two input shapes:

- Normal `argc/argv` from the shell.
- A single command string, used by file-reading mode.

For a single command string, it:

- strips comments beginning with `#`,
- collapses whitespace,
- joins tokens after commas by removing spaces after comma-separated syntax,
- allocates one block containing both pointer array and copied argument strings.

For normal shell arguments, it joins adjacent arguments when an argument ends in `,`, preserving legacy comma-list syntax.

The resulting `av` array is mutable and NUL-terminated, which is required by downstream parsers that mutate argument strings.

## Option Parsing

For `ipfw`, `ipfw_main()` handles options:

- `-a`: show accounting counters,
- `-b`: comment-only compact mode,
- `-c`: compact mode,
- `-d`: display dynamic rules,
- `-D`: dynamic-only display/delete,
- `-f`: force,
- `-h`: help,
- `-i`: show table values as IP,
- `-n`: test-only,
- `-N`: resolve names,
- `-p`: rejected here because command-file preprocessing requires an absolute pathname mode,
- `-q`: quiet,
- `-s`: sort field,
- `-S`: show sets,
- `-t`/`-T`: timestamp display,
- `-v`: verbose,
- `-x`: binary debug output.

For `dnctl`, it handles `-h`, `-n`, `-s`, and `-v`.

If not already forced, non-interactive stdin sets `g_co.do_force`.

## Command Dispatch

`ipfw_main()` supports historical syntax where a rule number precedes `add`, swapping the first two arguments to normalize.

It detects command domains:

- `nat`
- `pipe`
- `queue` / `flowset`
- `sched`
- `set N`

For `pipe`/`queue`/`sched`/`nat`, it also normalizes `pipe N config` into `pipe config N` for easier parsing.

Primary dispatch includes:

- `ipfw_add()`
- `ipfw_show_nat()`
- `ipfw_config_pipe()`
- `ipfw_config_nat()`
- `ipfw_sets_handler()`
- `ipfw_table_handler()`
- `ipfw_sysctl_handler()` for `enable`/`disable`
- `ipfw_delete()`
- NAT64 and NPTv6 handlers
- `ipfw_flush()`
- `ipfw_zero()`
- `ipfw_list()`
- `ipfw_internal_handler()`

For `dnctl`, commands outside the dummynet domain fall back to help.

## Command File Mode

`ipfw_readfile()` is used when the last CLI argument is an absolute readable path. It supports options that can apply globally before the file name:

- for `ipfw`: `-c`, `-f`, `-N`, `-n`, `-p`, `-q`, `-S`
- for `dnctl`: `-n`, `-q`

With `-p`, it runs a preprocessor command with the file as stdin and reads commands from the preprocessor stdout. It uses `pipe()`, `fork()`, `dup2()`, `execvp()`, `fdopen()`, and `waitpid()`.

Each input line is passed to `ipfw_main(2, args)` as a single mutable string. `setprogname()` is changed to `Line N` while processing, improving diagnostics for file lines.

## Dependencies

`main.c` is the only file in this group with the actual C `main()`. It depends on handler and global declarations from `ipfw2.h`, especially:

- `g_co`
- `is_ipfw()`
- command handler prototypes
- `resvd_set_number`
- `_substrcmp()`

## Error Handling and Risks

The file generally exits with `errx()`/`err()` on invalid usage, unreadable files, fork/pipe/exec errors, and preprocessor failure.

Important behavioral caveats:

- `g_co` is global and not reset between command-file lines. The header explicitly documents this; options in one line can affect later lines.
- The single-string parser mutates the original input line; this is required for downstream parsing but means the string must not be immutable storage.
- File mode is triggered only by an absolute pathname in the last argument. Relative command files are not treated as file mode by `main()`.
- `-p` in normal command mode is rejected; preprocessing is only meaningful through `ipfw_readfile()`.
- Preprocessor argument handling rewrites `av[ac-1] = NULL` and passes the remaining arguments to `execvp()`, so command-file `-p` syntax depends on exact argument positioning.

## Testing Notes

Useful tests:

- Basename-driven `ipfw` versus `dnctl` dispatch.
- One-string parsing with comments, whitespace, and comma-separated operands.
- Shell-argv comma joining.
- Legacy `100 add ...` normalization.
- `pipe N config` and `pipe config N` equivalence.
- Command-file mode with and without preprocessor, including preprocessor nonzero exit and signal termination.
- Persistence of global options across file lines.
