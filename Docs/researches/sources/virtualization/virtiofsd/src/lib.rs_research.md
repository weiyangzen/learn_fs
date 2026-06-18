# File Research: sources/virtualization/virtiofsd/src/lib.rs

## Scope

Crate root for virtiofsd library modules and crate-wide protocol error type.

## Modules

Exports descriptor utilities, file traits, filesystem trait, FUSE ABI, ID maps, limits, macros, OS wrappers, passthrough filesystem, directory reading, sandbox, server, soft ID map, utilities, vhost-user backend, and optional seccomp support.

## Error Type

`Error` covers FUSE message decode/encode/flush failures, missing parameters/extensions, invalid C strings, invalid header length, and xattr size mismatch.

## Role

This file forms the library boundary used by `main.rs` and internal modules. Its error type is focused on protocol message handling rather than filesystem operation errors.
