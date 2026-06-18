# File Research: sources/os/linux/linux/fs/binfmt_script.c

Purpose: Implements the kernel `#!` script binary format handler.

Main behavior:
- `load_script()` accepts only files whose initial bytes are `#!`.
- It parses the first line of `bprm->buf` into interpreter path and optional single argument.
- It carefully handles non-NUL-terminated buffers and rejects cases where the interpreter path may be truncated.
- It permits truncated interpreter arguments because the interpreter can reopen and parse the script itself.
- It rejects execution when `BINPRM_FLAGS_PATH_INACCESSIBLE` is set, because the interpreter usually needs to open the script by path.

Argument rewriting:
- Removes the original argv[0].
- Pushes the script filename, optional interpreter argument, and interpreter path in reverse order.
- Calls `bprm_change_interp()` to update the interpreter name.
- Opens the interpreter with `open_exec()` and stores it in `bprm->interpreter`.

Registration:
- `script_format` registers `load_script` through `register_binfmt()` at `core_initcall`.
- Module exit unregisters the format.

Risk notes: The key edge cases are first-line truncation, whitespace trimming, optional argument splitting, and path-inaccessible scripts such as `/dev/fd/...` with close-on-exec descriptors.
