# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/fns.h

## Role

Declares cross-file functions and globals for the `nusb/usbd` implementation.

## API Surface

The header exposes the global hub list and functions for attach/detach events, hub polling work, hub creation, stable-name hashing, stable-name assignment, idle checking, and hub port feature control.

It is the small connection point between `hub.c`, `usbd.c`, and `hname.c`.
