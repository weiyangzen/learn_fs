# sources/test-tools/strace/src/gen/generated.h

Generated umbrella header for generated decoder fragments. It includes `defs.h` and exposes generated declarations needed by generated source such as `gen_hdio.c` and consumers like `hdio.c`. It owns no runtime state or control flow. Dependencies are the generator pipeline and the generated C files staying synchronized. Risks are stale declarations after regeneration or manual edits breaking generated include order. Test signals are clean builds after running generator scripts and successful inclusion by generated decoder translation units.
