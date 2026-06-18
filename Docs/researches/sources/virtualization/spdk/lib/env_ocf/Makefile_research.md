# File Research: sources/virtualization/spdk/lib/env_ocf/Makefile

Builds the SPDK OCF environment library `ocfenv`.

Important behavior:
- Uses `CONFIG_OCF_DIR`/`CONFIG_OCF_PATH` to integrate Open CAS Framework sources.
- If `CONFIG_CUSTOMOCF=y`, copies a prebuilt OCF library into the SPDK static library path.
- Otherwise invokes the OCF make targets to export headers and sources into `lib/env_ocf`, then builds local C sources.
- `clean` removes exported OCF `include` and `src` directories plus generated objects/library.
- `exportlib` copies the built library to a caller-provided `O=` path.

Role: bridges SPDK's build system with either OCF source builds or precompiled OCF artifacts.
