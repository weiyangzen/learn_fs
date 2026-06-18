# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Clog.c

Console print wrappers.

`consVPrint` formats into a fixed buffer and writes through `consWrite`; `consPrint` is the varargs wrapper. A disabled `syslog` block shows the intended future path but avoids noisy filesystem-check logging.
