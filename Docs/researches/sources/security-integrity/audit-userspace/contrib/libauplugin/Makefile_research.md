# sources/security-integrity/audit-userspace/contrib/libauplugin/Makefile

Purpose: Minimal standalone build recipe for the `auplugin-example` sample using installed audit libraries rather than the autotools tree.

Important APIs and targets: Defines `CFLAGS=-g -W -Wall -Wundef`, `LIBS=-lauplugin -lauparse -laudit`, `all` compiling `auplugin-example.c`, and `clean` removing the binary and object files.

Control flow: `make` invokes a single `gcc` command. `make clean` deletes generated local artifacts.

State and persistence: Persists only the compiled `auplugin-example` binary and any `*.o` files.

Dependencies and integration: Requires system headers/libraries for `libauplugin`, `libauparse`, and `libaudit` in the compiler's default search paths. It is a contrib example, not an installed automake target in this file.

Risks: No include/library path customization, no dependency tracking, no hardening flags, and no install target. It assumes library ABI compatibility with the source example.

Test signals: `make clean && make` should link successfully against installed audit libraries. Running the binary with raw audit records should exercise `auplugin-example.c`.
