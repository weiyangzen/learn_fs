# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/meson.build

This Meson file defines developer-only targets for regenerating or checking generated accessor files.

Targets:
- `update-common-accessors` runs `update-accessors.sh` to generate common accessor outputs:
  - `src/nvme/accessors.h`
  - `src/nvme/accessors.c`
  - `src/accessors.ld`
  - SWIG output `libnvme/accessors.i`
  - dict table output `libnvme/fctx_field_tables.h`
  - input `src/nvme/private.h`
  - nested source `src/nvme/private-fabrics.h`
- `update-fabrics-accessors` does the same for fabrics-specific accessors:
  - `src/nvme/accessors-fabrics.h`
  - `src/nvme/accessors-fabrics.c`
  - `src/accessors-fabrics.ld`
  - SWIG output `libnvme/accessors-fabrics.i`
  - input `src/nvme/private-fabrics.h`
  - nested source `src/nvme/private.h`
- `alias_target('update-accessors', ...)` runs both.

Behavior:
- Uses `python3` and `generate-accessors.py`.
- Adds `--check` when Meson option `check-accessors` is enabled, making the wrapper read-only for CI drift checks.
- Targets are not build-by-default; developers run `meson compile -C <build-dir> update-accessors`.

Integration:
- Included from `libnvme/meson.build` before library source setup so generated code paths are known.
