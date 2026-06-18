# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdouble.c

Implements double-precision arithmetic operators using 8-byte strings as double containers.

Key behavior:
- Provides double arithmetic, unary math, transcendental functions, comparisons, and conversions.
- Accepts integers, reals, and readable 8-byte strings as operands; result-producing operators require a writable 8-byte string.
- Implements `.dadd`, `.ddiv`, `.dmul`, `.dsub`, `.dabs`, `.dceiling`, `.dfloor`, `.dneg`, `.dround`, `.dsqrt`, `.dtruncate`, `.darccos`, `.darcsin`, `.datan`, `.dcos`, `.dexp`, `.dln`, `.dlog`, `.dsin`.
- Conversion operators parse strings to doubles, convert to integer/real, and format doubles to strings.
- Checks division by zero, invalid powers, log/sqrt domains, string syntax, and target buffer sizes.

Dependencies:
- Uses math portability wrappers and Ghostscript numeric/operator helpers.

Research notes:
- Double values are represented in host binary format inside strings, so portability depends on caller and platform agreement.
