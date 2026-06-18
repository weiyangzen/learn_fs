# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/mod.mk

Common make fragment for PAM modules. It marks each library as a loadable module, builds static and link libraries, disables link installation, includes shared PAM settings, and installs modules under `/usr/lib[/<mlib>]/security`.

It sets warning level 6 and then includes `bsd.lib.mk`.
