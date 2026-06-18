# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/fedora.c

Static helper binary installed into the phony Fedora image as `/bin/sh`, `/bin/rpm`, and `/sbin/dracut`.

Key behavior:
- Detects behavior from `argv[0]` basename.
- As `rpm -ql kernel-*`, prints hard-coded kernel/module paths matching `make-fedora-img.pl`.
- As `dracut`, exits successfully without doing anything.
- As `sh -c COMMAND`, performs a simple split on spaces/tabs and quoted strings, then `execvp`s the parsed command.
- For any unexpected invocation, prints all argv entries and exits failure.

Research notes:
- This is intentionally minimal behavior to satisfy tools such as `virt-v2v` inside generated test images.
