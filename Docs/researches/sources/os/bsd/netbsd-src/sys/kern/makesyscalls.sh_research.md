# File Research: sources/os/bsd/netbsd-src/sys/kern/makesyscalls.sh

Read completely: 1277 lines.

Generates NetBSD syscall interface artifacts from a configured `syscalls.master`-style input file. The shell wrapper sources a config file, validates numeric settings such as `nsysent` and `maxsysargs`, prepares temporary output fragments, normalizes input with `sed`, and then runs a large embedded `awk` program that parses syscall table rows and emits C headers, switch tables, names arrays, autoload metadata, DTrace syscall-provider helpers, and rump syscall marshalling code.

Configuration contract:
- Required or expected config variables include `sysnames`, `sysnumhdr`, `syssw`, `sysautoload`, `sysarghdr`, `systrace`, `compatopts`, `switchname`, `namesname`, `constprefix`, `emulname`, `registertype`, `nsysent`, `sysalign`, and rump output paths.
- Defaults include `sys_nosys=sys_nosys`, `maxsysargs=8`, and `/dev/null` outputs for optional systrace/autoload/rump files.
- `addsuffix()` preserves `/dev/null` targets while deriving fragment filenames for normal outputs.

Input processing and parser behavior:
- The pre-awk `sed` pass strips dollar signs, joins backslash-continued lines, and inserts spaces around `{}`, `()`, `*`, `|`, and commas for easier token parsing.
- The awk script tracks syscall numbers, conditional nesting, and compatibility wrappers; it reports hard errors for out-of-sync syscall numbers, malformed prototypes, unbalanced preprocessor conditionals, and unknown syscall keywords.
- `parseline()` handles row modifiers including `INDIR`, `MODULAR`, `RUMP`, syscall aliases, compatibility suffixes, return type, function prefix/base name, fixed arguments, varargs, and padding/alignment expectations.
- Keywords routed to full entries include `STD`, `NODEF`, `NOARGS`, `INDIR`, `NOERR`, `EXTERN`, and configured compatibility keywords. `OBSOL`, `UNIMPL`, `EXCL`, and `IGNORED` produce filler or nullop/nosys entries.

Generated kernel/user artifacts:
- `sysnumhdr` receives syscall number macros, max argument macros, prototype comments used by libc lint stub generation, and final `MAXSYSCALL`/`NSYSENT` definitions.
- `sysarghdr` receives `syscallarg` ABI wrapper definitions, argument structures, compile-time size checks, and syscall prototypes.
- `syssw` receives `struct sysent` entries with argument counts, byte sizes, function pointers, and flags such as indirect, pointer-argument, 64-bit argument, 64-bit return, wide-return, and modular-autoload markers.
- `sysnames` receives both kernel-visible include handling and userland-friendly primary/alternate syscall names arrays.
- `sysautoload` receives `struct sc_autoload` entries for modular syscalls and terminates with a `{ 0, NULL }` sentinel.

Rump and tracing generation:
- Rump output includes syscall wrappers, public/renamed prototypes, `rump_sysent`, `rump_sysent_nomodbits`, `rumpns_sysent` aliasing, and a syscall map file.
- Rump wrappers convert user-facing arguments into generated syscall argument structures using endian-sensitive `SPARG`, issue `rumpclient_syscall` or `rump_syscall`, translate errno, and reconstruct return values from `register_t retval[2]`.
- The `pipe` syscall is handled specially because it returns two file descriptors through `retval`.
- DTrace output includes `systrace_args`, entry argument descriptions, and return argument descriptions. Pointer-like types are cast appropriately for register-array extraction.

Compatibility and ABI details:
- Compatibility wrappers are generated from `compatopts` with preprocessor-controlled macros that either call the compatibility function namespace or `sys_nosys`.
- `uncompattypes` maps selected old ABI structure names such as `timeval50`, `timespec50`, `stat30`, and `kevent100` to modern public rump prototype types.
- `isarg64()` and `isretwide()` encode syscall dispatch metadata for 64-bit arguments and ABIs that need careful sign extension of 32-bit results on wide registers.
- The script enforces optional 64-bit argument alignment for `off_t`, `dev_t`, and `time_t`, with an explicit exception for `sys_posix_fadvise`.

Risks and notes:
- This is build-critical generated-code infrastructure; parse errors or config variable mistakes can corrupt multiple generated ABI surfaces at once.
- The parser is whitespace/token sensitive after the custom `sed` preprocessing pass, so unusual type syntax can break generation unless it matches the expected grammar.
- Allocation-size checks depend on `maxsysargs` and generated `check_syscall_args`; invalid syscall signatures can fail at generation time or compile time.
- Rump syscall generation assumes integral return types and has special-case compatibility behavior, so new syscall types may require script changes.
- Temporary files are removed by a trap, but generation writes many partial outputs before final concatenation; interrupted or failed builds should rely on the build system to avoid stale generated files.
