# File Research: sources/virtualization/nvme-cli/unit/meson.build

Meson definition for C unit tests.

Targets:
- `test-uint128` using `test-uint128.c`, `util/types.c`, and `util/suffix.c`.
- `test-suffix-si-parse` using `util/suffix.c`.
- `test-suffix-binary-parse` using `util/suffix.c`.
- `test-uint128-si` using `util/types.c` and `util/suffix.c`.
- `test-argconfig-parse` using `util/argconfig.c` and `util/suffix.c`.

Dependencies:
- `config_dep`, `ccan_dep`, and `libnvme_dep`.

Role:
- Adds focused parser/formatting tests to Meson’s test suite.
