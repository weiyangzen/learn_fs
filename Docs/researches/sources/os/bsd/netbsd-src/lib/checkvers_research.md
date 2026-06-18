# File Research: sources/os/bsd/netbsd-src/lib/checkvers

Korn shell wrapper around `checkver`. It finds all `shlib_version` files below the current directory and invokes `checkver` for each, reusing a single library list built from `-d`, `-s`, or `-f`.

It suppresses duplicate headers after the first failure, tracks whether a library name was encountered multiple times, and warns with previous/current source locations. It exits `2` for usage or `checkver` failures and `1` if any library version mismatch is found.

Notable source behavior: the quiet test is written `[ quiet -eq 1 ]`, lacking `$`, so the intended `quiet` variable check is not actually expressed correctly.
