# File Research: sources/os/linux/linux/fs/dlm/rcom.h

## Role

`rcom.h` declares recovery communication APIs.

## Interface

It exposes status/name RCOM requests, master lookup and lock-copy sends, the RCOM receive dispatcher, and the not-ready status reply helper.

## Research Notes

Read completely. The declarations correspond to `rcom.c` and are consumed by recovery, directory, and receive paths.
