# sources/test-tools/syzkaller/tools/syz-usbgen/usbgen.go

## Purpose

`usbgen.go` parses kernel syslog lines containing generated USB and HID IDs and emits a Go source file with driver-to-ID maps for Linux virtual USB initialization.

## Important APIs, Types, and Functions

Functions are `main`, `extractIds`, `generateIdsVar`, and `usage`. The tool uses regular expressions for `USBID` and `HIDID` lines, `hex.DecodeString`, `maps.Keys`, `slices.Sorted`, `slices.Sort`, `osutil.WriteFile`, and `tool.Failf`.

## Control Flow

`main` requires input and output paths, reads syslog bytes, extracts 34-character USB IDs and 24-character HID IDs, generates a Go file header, appends `usbIds` and `hidIds` variables plus aggregate strings, and writes the output. `extractIds` deduplicates identical matching log lines and groups IDs by driver. `generateIdsVar` sorts drivers and IDs for stable output and formats decoded byte strings as concatenated Go string literals.

## State and Persistence Behavior

It reads one syslog file and overwrites one generated Go file. It prints counts to stdout but does not persist metadata beyond the generated source.

## Dependencies and Integration Points

The generated file targets `package linux` and is referenced by Linux USB external fuzzing setup. The input format is tied to kernel log prefixes emitted by USB/HID ID discovery code.

## Risks and Test Signals

The driver capture regex is greedy and trusts log formatting. Invalid hex is fatal despite the regex restricting lowercase hex. Empty input generates empty aggregate strings. Tests should cover duplicate log lines, multiple drivers, sort stability, no-match output, malformed sizes, and generated Go compilation.
