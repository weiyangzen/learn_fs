# File Research: sources/virtualization/nbdkit/plugins/curl/Makefile.am

This Automake file builds `nbdkit-curl-plugin.la` when libcurl is available and the platform is not Windows, because the implementation uses a self-pipe. Sources are `config.c`, `curldefs.h`, `curl.c`, `scripts.c`, `times.c`, `worker.c`, and the public plugin header.

The module includes public/generated headers, common include files, replacements, and utilities. It compiles with `$(CURL_CFLAGS)` and links common utilities, compatibility replacements, the platform import library, and `$(CURL_LIBS)`. Optional plugin symbol versioning uses `plugins/plugins.syms`.

Documentation generation builds `nbdkit-curl-plugin.1` and HTML from POD, inserting the shared magic-parameter text.
