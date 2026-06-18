# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbtx.h

Header for ByteTranslate encode/decode filters.

It defines `stream_BT_state`, used for both encode and decode, with common stream state and a 256-byte translation table. It declares the GC descriptor macro and external templates `s_BTE_template` and `s_BTD_template`.

The implementation is elsewhere. This is a simple byte-mapping filter interface, not filesystem code.
