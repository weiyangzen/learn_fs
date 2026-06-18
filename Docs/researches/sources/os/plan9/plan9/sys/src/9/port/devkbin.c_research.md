# File Research: sources/os/plan9/plan9/sys/src/9/port/devkbin.c

Implements `#Ι/kbin`, a privileged write-only keyboard scan-code injection device. It exists to let external keyboard sources, such as USB keyboard handling, feed scan codes into the kernel keyboard map path without duplicating map processing.

The namespace is just a directory and `kbin`. Only `eve` may open it. The file is exclusive via `kbinbusy`, protected by `kbinlck`.

Writes iterate over input bytes and call `kbdputsc(byte, 1)`, marking them as external source input. Reads on the data file return EOF; directory reads use the normal device directory helper.

The device is intentionally narrow and depends on the external keyboard scan-code consumer `kbdputsc`.
