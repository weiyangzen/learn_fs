# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/Makefile.inc

This make include adds the internal ReFUSE compatibility implementation files to `SRCS` and installs the internal compatibility headers through `INCS`. It includes buffer, channel, filesystem stacking, legacy, poll, session, and version-specific source/header files.

Integration points: pulled into the librefuse build from the parent makefile. Risk is build/export drift: adding a new compatibility version requires updating both `SRCS` and `INCS` consistently.
