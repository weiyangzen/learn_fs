# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/devpost.add/devpost.add.mk

This makefile installs additional devpost font files into a configurable `FONTDIR/devpost` directory. It creates directories with configured ownership/group/mode, copies `FONTFILES`, and includes a `changes` target to rewrite configuration values.
