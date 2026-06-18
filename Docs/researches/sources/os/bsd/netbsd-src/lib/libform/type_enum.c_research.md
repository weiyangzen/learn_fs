# File Research: sources/os/bsd/netbsd-src/lib/libform/type_enum.c

Defines builtin `TYPE_ENUM`.

Arguments are a null-terminated choices array plus `ignore_case` and `exact` flags. The implementation counts choices at argument creation and uses `match_enum` to compare trimmed field input against trimmed choices.

Field validation replaces buffer 0 with the matched canonical choice. Choice callbacks implement wraparound next/previous selection using the current field buffer. Matching supports exact-length mode or prefix-style mode depending on `exact`.
