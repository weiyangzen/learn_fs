# File Research: sources/virtualization/nvme-cli/libnvme/test/utils.h

This header declares common libnvme test utility functions:
- `FILE *test_setup_log(void);`
- `void test_print_log_buf(FILE *logfd);`
- `void test_close_log(FILE *fd);`

It uses `#pragma once` and includes `<stdio.h>` for `FILE`.

Integration:
- Paired with `utils.c`.
- Intended for tests with strict setup failure handling.
