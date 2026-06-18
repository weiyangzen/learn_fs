# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_rgrp.c

This file contains Check unit tests for resource-group planning, bitmap search, and final RG write behavior.

The fixture `mockup_rgrps()` creates a 1 GiB temporary mock device, initializes an `lgfs2_sbd`, plans resource groups, creates the first rindex entry, appends a resource group, allocates bitmap buffers, and stores it in `tc_rgrps`. `teardown_rgrps()` closes/free resources and bitmap buffers.

Test cases:
- `test_rbm_find_good()` verifies `lgfs2_rbm_find()` can find free extents from size 1 through the whole RG.
- `test_rbm_find_bad()` verifies requesting an extent larger than the RG data area fails.
- `test_rbm_find_lastblock()` marks all blocks allocated except the final block and verifies the search finds that last free block.
- `test_rgrps_write_final()` verifies `lgfs2_rgrps_write_final()` writes a valid final RG header with `rg_skip == 0`, and returns `-1` on an invalid fd.

`suite_rgrp()` groups rbm search tests and final-write tests with fixtures.

Risks and notes:
- `test_rbm_find_good()` disables timeout because it can iterate many extent sizes.
- The tests validate both in-memory bitmap manipulation and actual pwrite/pread behavior against a temporary file.
