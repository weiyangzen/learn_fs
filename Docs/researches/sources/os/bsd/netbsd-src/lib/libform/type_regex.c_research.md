# File Research: sources/os/bsd/netbsd-src/lib/libform/type_regex.c

Defines builtin `TYPE_REGEXP`.

Argument creation compiles the supplied expression with `regcomp` using `REG_EXTENDED | REG_NOSUB | REG_NEWLINE`. Copies share the compiled regex by incrementing a reference count. Free decrements the count and frees storage at zero.

Field validation runs `regexec` against the field buffer. There is no character-level validation.
