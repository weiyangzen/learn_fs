# File Research: sources/virtualization/nbd/man/nbd-server.1.sgml.in

DocBook manpage template for `nbd-server(1)`.

It describes serving a file or block device over NBD, with support for diskless clients, swap, and filesystem use over exported storage. It documents legacy command-line export configuration while noting that configuration files are preferred.

Options cover listen address/port, exported filename, size, read-only, multifile, copy-on-write, auth host list, config file, max connections, version, foreground/no-fork modes, and conversion of command-line options to a config section.

It also documents SIGHUP behavior: re-reading config adds newly defined exports but does not modify existing served exports.
