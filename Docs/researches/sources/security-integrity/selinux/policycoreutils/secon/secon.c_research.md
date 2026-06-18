<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/secon.c -->
# sources/security-integrity/selinux/policycoreutils/secon/secon.c

## Purpose
Displays selected fields from SELinux security contexts obtained from arguments, stdin, current process state, parent/pid process state, files, or symlinks.

## Important APIs, Types, And Functions
The option state lives in a single bitfield struct `opts`. Important functions are `cmd_line()`, `get_scon()`, `my_getXcon_raw()`, `disp__color_to_ansi()`, `disp__con_color_ansi()`, `disp__con_val()`, and `disp_con()`. It uses libselinux APIs such as `getcon_raw`, `getexeccon_raw`, `getfscreatecon_raw`, `getkeycreatecon_raw`, `getpidcon_raw`, `getfilecon_raw`, `lgetfilecon_raw`, context translation, `context_new`, and `selinux_raw_context_to_color`.

## Control Flow
`cmd_line()` toggles requested fields (`user`, `role`, `type`, sensitivity, clearance, range), output modes (`raw`, prompt, color), and input source. If no source is provided it defaults to current process or stdin when piped. `get_scon()` reads or queries a raw context. `disp_con()` translates to display context unless raw mode is requested, optionally loads color information, parses fields with `context_new`, and prints either labeled multiline output or prompt-style colon-separated output.

## State And Persistence
The tool is read-only. It reads `/proc/<pid>/attr/{exec,fscreate,keycreate}` directly for process attributes not wrapped by libselinux APIs.

## Dependencies And Integration Points
It integrates with libselinux context parsing/translation and `/proc` process attributes, and is used by scripts for field extraction.

## Risks And Edge Cases
`atoi()` pid parsing accepts malformed input as zero. Color parsing assumes a fixed token sequence. Empty exec/fs/key contexts are represented as empty strings. Context translation failures abort.

## Test Signals
Cover field combinations, raw versus translated output, stdin input, file versus symlink labels, current and parent process modes, prompt/color output, missing SELinux, and invalid context strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/secon.c -->
