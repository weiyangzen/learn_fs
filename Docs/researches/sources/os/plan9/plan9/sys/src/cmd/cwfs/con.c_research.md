# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/con.c

Console command dispatcher for the cached-WORM file server. It owns the in-memory command table, console flag table, initial console session setup, and many administrative commands exposed on the server console.

Key responsibilities:
- `consserve()` initializes command handlers, runs initial commands (`cfs`, `users`, `version`), optionally touches the cw superblock, then starts `consserve1`.
- `cmd_install()` and `flag_install()` append entries, sort them by command/flag name, and return bit flags for per-channel/global tracing.
- `cmd_exec()` tokenizes a single console command line into up to 10 argv slots and dispatches the matching command.
- Admin commands include `halt`, `sync`, `help`, `who`, `hangup`, `stats`, `stata`, `flag`, `cfs`, `version`, `profile`, `files`, `noattach`, `allow`, `disallow`, and user/file maintenance commands.
- File repair helpers include `walkto()`, `cmd_fstat()`, `cmd_create()`, `cmd_clri()`, `cmd_remove()`, `cmd_clean()`, `doclean()`, and `ckblock()`.
- `number()` parses signed integer strings into `vlong`, preserving support for large block numbers.

Important interactions:
- Uses console 9P wrappers from `console.c` (`con_attach`, `con_clone`, `con_walk`, `con_create`, etc.).
- Uses global `cons`, `chans`, `files`, `mainlock`, `mballocs`, `tagnames`, and permission toggles such as `wstatallow`, `writeallow`, `duallow`, `noattach`.
- Installs flags used elsewhere: `attachflag`, `chatflag`, `errorflag`, `whoflag`, `authdebugflag`, `authdisableflag`.

Research notes:
- The command table has fixed capacity (`command[100]`) and flag table fixed capacity (`flag[35]`, with hard limit `i >= 32` in `flag_install`).
- `cmd_time()` builds a command string from argv and measures elapsed time with `time(nil)`/`TK2MS`, but this server defines `HZ` as 1, so timing granularity is coarse.
- `cmd_clean()` can print and optionally rewrite direct or indirect block pointers in a file's `Dentry`; it refuses mutation on `Devro`.
- `walkto()` uses console fids `FID1` and `FID2`, clones from the current root, then walks slash-separated path components.
