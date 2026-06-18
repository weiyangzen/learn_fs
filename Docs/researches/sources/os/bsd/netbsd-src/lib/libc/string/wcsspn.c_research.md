# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsspn.c

Implements `wcsspn(s, set)`, returning the length of the initial segment of `s` consisting only of characters in `set`. It uses a simple nested scan over the accept set for each input character.

Stops at the first character not present in `set`.
