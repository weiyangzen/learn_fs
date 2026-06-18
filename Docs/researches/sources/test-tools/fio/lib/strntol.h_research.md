# sources/test-tools/fio/lib/strntol.h

Purpose: declares bounded string-to-long conversion.

Important APIs/functions: `long strntol(const char *str, size_t sz, char **end, int base)`.

Control flow/state: no header state; callers provide an explicit slice length and optional end pointer.

Dependencies/integration: includes `stdint.h` but the signature also relies on `size_t` being available from prior includes in some translation units.

Risks/test signals: the missing direct include for `stddef.h` can be fragile if included standalone. Compile tests should include this header in isolation.
