# File Research: sources/os/plan9/plan9/sys/src/cmd/con/hayes.c

Hayes-compatible modem dialer.

It opens an optional serial device plus its `ctl` file, sends attention/reset/setup AT commands, chooses pulse or tone dialing, waits for modem result lines, parses `CONNECT` speed, and writes baud plus modem flow control to the control file. `readmsg` polls available input via `dirfstat` with a timeout and classifies known result prefixes as OK, success, failure, or noise.

The command is designed to be used with Plan 9 serial devices and can use stdout/stdin as the modem data stream when no device argument is supplied.
