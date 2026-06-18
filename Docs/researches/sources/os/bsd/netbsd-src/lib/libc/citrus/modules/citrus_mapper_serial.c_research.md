# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.c

Read completely: 263 lines.

This module implements two composite mapper plugins: serial and parallel. Both parse a comma-separated list of mapper names and open each mapper from the current mapper area.

Key behavior: serial conversion applies every mapper in order, feeding each output into the next. Parallel conversion tries each mapper against the original source and returns the first successful result; `ILSEQ` aborts immediately, while other failures continue until returning non-identical. Initialization rejects child mappers that are not stateless 1:1 converters.

Important interactions: uses `_mapper_open`, `_mapper_close`, mapper trait accessors, memstream parsing, and SIMPLEQ storage.

Security/reliability notes: `parse_var` trims mapper names into a `PATH_MAX` buffer with `snprintf` but does not detect truncation. In one error path after opening a child mapper with incompatible traits, it frees the link without closing `ml_mapper`, causing a resource leak on malformed composition definitions.
