# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testtime.c

Small test program for SMB/NT time conversion.

Key points:
- With an argument, treats it as NT FILETIME and prints converted Plan 9 seconds and `ctime`.
- Without arguments, converts a fixed Plan 9 timestamp to NT time and back, printing both.

Dependencies:
- Uses `smbplan9time2time` and `smbtime2plan9time`.

Notable behavior:
- Hardcoded default timestamp is `1032615845`.
