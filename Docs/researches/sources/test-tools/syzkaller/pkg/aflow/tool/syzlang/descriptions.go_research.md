# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions.go

## Purpose
Exposes Linux syzlang description files to aflow agents.

## Important APIs, Types, and Functions
`DescriptionFiles` lists embedded `sys/linux` entries from `sys.Files`. `ReadDescription` registers a `read-description` tool. `readDescription` reads a requested file and returns its contents.

## Control Flow
Listing reads the Linux sys directory and panics on embedded filesystem errors. Reading joins `targets.Linux` with the user-supplied file using slash paths, reads from embedded files, and converts errors to bad-call errors.

## State and Persistence Behavior
Read-only access to embedded syzlang files. No runtime persistence.

## Dependencies and Integration Points
Depends on `aflow`, `sys.Files`, and `targets.Linux`. Used by syzlang-focused agents building or validating repro programs.

## Risks and Test Signals
Risk is path handling across embedded FS paths and user-requested missing files. Tests assert many descriptions, presence of `sys.txt`, successful read, and missing-file error.
