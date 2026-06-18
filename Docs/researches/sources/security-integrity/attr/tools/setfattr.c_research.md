## sources/security-integrity/attr/tools/setfattr.c

Purpose: modern CLI for setting/removing/restoring Linux xattrs.

It parses `-n/-v` set, `-x` remove, `-h` no-dereference, `--restore`, `--raw`, version/help, then applies `setxattr/lsetxattr` or remove variants. Restore mode consumes `getfattr -d` style `# file:` blocks, unquotes paths/names, decodes text/hex/base64 values unless raw, and sets/removes attributes. State includes global operation flags, static decode/path buffers, and error counters. Dependencies are libmisc quote/unquote/line/allocation helpers, Linux xattr syscalls, getopt, gettext. Risks include in-place unquote of option strings, complex base64 validation, restore status overwritten by later attributes, no create/replace flags, and following symlinks by default. Tests should cover all encodings, raw mode, restore files, deletion, symlink mode, and malformed input.
