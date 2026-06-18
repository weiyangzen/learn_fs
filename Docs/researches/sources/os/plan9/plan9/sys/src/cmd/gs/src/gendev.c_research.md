# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gendev.c

Read status: complete.

Purpose: build-time tool that generates `.dev` configuration files from command-line resource arguments.

Usage model:
- Supports `-d <devfile>`, `-m <modfile>`, and `-a <modfile>` for device/module file generation or append mode.
- Supports options `-Z`, `-n`, and `-C`.
- Accepts resource category switches followed by item names.

Main logic:
- Creates or appends to `<name>.dev`.
- Emits an include guard using the output file name and current file position.
- Optionally adds the device itself when generating a device file.
- Writes generated resource macros under `#ifndef RES_SCAN`.
- For `uniq_last` resources, emits a second `RES_SCAN` pass to track the final occurrence.
- Handles categories including `dev`, `dev2`, `emulator`, `font`, `include`, `init`, `iodev`, `lib`, `obj`, `oper`, and `ps`.

Important functions:
- `add_entry` maps category/item pairs into generated macro lines.
- `write_item` emits normal resource lines with category `#ifdef` guards and uniqueness guards.
- `write_scan_item` emits `SEEN` definitions for last-occurrence detection.

Filesystem/storage relevance:
- Writes build module-description files.
- No runtime filesystem implementation.

Notable behavior and risks:
- Source comments state it does not handle `-replace` and does not merge `device` and `device2`.
- Uses fixed 80/100 byte buffers for generated strings and names.
- `main` has old-style implicit `int` declaration style.
