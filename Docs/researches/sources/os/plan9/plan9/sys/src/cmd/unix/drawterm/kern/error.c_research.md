# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.c

Defines global error string objects used throughout the drawterm kernel device and namespace code.

Contents:
- Common namespace/device errors such as `Enonexist`, `Eexist`, `Enotdir`, `Eisdir`, `Ebadsharp`, and `Eperm`.
- I/O and resource errors such as `Eio`, `Ehungup`, `Etimedout`, `Enomem`, and `Enofd`.
- Mount and union errors such as `Emount`, `Eunmount`, `Eunion`, and `Emountrpc`.
- Control and stat errors such as `Ebadctl`, `Ebadarg`, `Eshortstat`, `Ebadstat`, and `Ecmdargs`.

Role:
- Provides stable string addresses and text for `error()` calls.
