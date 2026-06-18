# sources/user-network-fs/libfuse/lib/helper.c

Purpose: `helper.c` implements convenience entry points for standalone high-level FUSE programs: command-line parsing, default subtype/fsname handling, daemonization, mount/session setup, loop selection, service-mode main flow, and connection option parsing.

Important APIs, types, and functions: Public APIs include `fuse_cmdline_help`, versioned `fuse_parse_cmdline` implementations, `fuse_main_real_versioned`, compatibility `fuse_main_real_30`, service-mode `fuse_service_main_real_versioned`, `fuse_apply_conn_info_opts`, `fuse_parse_conn_info_opts`, and `fuse_open_channel`. Internal option tables are `fuse_helper_opts` and `conn_info_opt_spec`, with `struct fuse_conn_info_opts` carrying parsed capability and numeric connection settings.

Control flow: Normal `fuse_main_real_versioned` parses args, handles help/version, validates mountpoint, starts early daemonization when needed, creates the high-level `struct fuse`, mounts it, installs signal handlers, marks daemonization success, runs single-threaded or multithreaded loop, then unmounts/destroys and frees args. Service mode parses service command lines, creates a high-level fuse object, configures loop settings, installs signals, asks `fuse_service_session_mount` to perform remote mount protocol, sends goodbye, releases the service, and runs the selected loop. Connection options parse into `fuse_conn_info_opts` and are later applied by setting/unsetting capability bits on `struct fuse_conn_info`.

State and persistence behavior: The helper mutates `struct fuse_args`, allocates/frees `opts.mountpoint`, starts daemonization state through `fuse_daemonize_*`, installs process signal handlers, and creates/destroys FUSE session/high-level objects. It does not persist filesystem data.

Dependencies and integration points: It connects `fuse_opt.c`, high-level `fuse.c`, low-level session APIs, mount utilities, daemonization helpers, signal handlers, multithreaded loop config, and optional service-mount APIs. It is the main bridge used by applications that call `fuse_main`.

Risks: Error-path result codes are user-visible and historically significant. Argument ownership is delicate because parsing may allocate and rewrite argv. Daemonization success must align with mount/init success. Service mode has extra release/goodbye paths and must avoid double-cleanup. The source currently shows a duplicated `fuse_helper_opt_proc_service) == -1)` line in the service parse block, which appears syntactically suspicious and should be caught by build tests.

Test signals: Tests should cover help/version paths, missing/bad mountpoints, default subtype/fsname insertion, debug implying foreground, loop config settings, daemonization early success/failure, signal handler failure cleanup, service-mode parse/mount/release paths, and connection option capability toggles.
