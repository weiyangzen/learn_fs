# File Research: sources/virtualization/nbd/autogen.sh

Bootstrap script for Autotools generation.

It runs with `set -ex`, first generates `systemd/nbd@.service.sh.in` by invoking `make -C systemd -f Makefile.am`, then executes `autoreconf -f -i`.

This script is used directly by CI before `./configure`.
