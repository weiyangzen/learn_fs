# File Research: sources/virtualization/libguestfs/daemon/yara.c

## Role
Implements daemon YARA rule loading, destruction, and internal scanning actions when libyara is available.

## Main Flow
- `do_yara_load()` receives a FileIn rules file into a temporary file.
- Initializes YARA once with `yr_initialize()`.
- Destroys any previously loaded rules.
- Attempts `yr_rules_load()` first, then compiles source rules with `yr_compiler_add_file()` if the file is not already compiled rules.
- `do_yara_destroy()` frees loaded rules.
- `do_internal_yara_scan()` opens a guest path under chroot and scans its file descriptor.

## Output
Matching rules are serialized as `guestfs_int_yara_detection` records containing path and rule identifier, then streamed through FileOut.

## Lifecycle
A destructor `yara_finalize()` destroys remaining rules and calls `yr_finalize()` on daemon exit.

## Filesystem/Storage Relevance
This file enables malware/signature scanning of guest filesystem files from inside the appliance.
