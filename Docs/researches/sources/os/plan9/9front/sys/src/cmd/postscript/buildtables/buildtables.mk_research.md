# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.mk

This makefile generates and installs the `buildtables` shell script and its man page. It patches path variables into `buildtables.sh`, installs under configurable PostScript binary/font/library directories, and includes a `changes` target to rewrite local configuration values into the makefile and man page.
