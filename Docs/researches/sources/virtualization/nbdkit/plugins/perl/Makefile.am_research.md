# File Research: sources/virtualization/nbdkit/plugins/perl/Makefile.am

## Purpose
Builds the embedded Perl plugin adapter and distributes its example script.

## Main Contents
When Perl support is available, defines `nbdkit-perl-plugin.la` from `perl.c` and the plugin header, includes Perl architecture headers and CFLAGS, links Perl loader options and nbdkit utility libraries, applies plugin module flags and optional linker script, and generates `nbdkit-perl-plugin.3`.

## Dependencies
Gated by `HAVE_PERL`; documentation generation is gated by `HAVE_POD`.

## Risks and Notes
Correct compilation depends on `PERL_CFLAGS`, `PERL_LDOPTS`, and `PERL_ARCHLIB` matching the embedded Perl runtime.
