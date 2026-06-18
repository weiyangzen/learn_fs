# sources/test-tools/liburing/test/cmd-discard.c

Purpose: destructive block-device coverage for `io_uring_cmd` discard. Important APIs are `io_uring_prep_cmd_discard`, `BLOCK_URING_CMD_DISCARD`, `BLKGETSIZE64`, `BLKSSZGET`, `BLKROSET`, `O_DIRECT`, `O_EXCL`, and aligned buffers.

Control flow: require a device/file argument, discover block geometry, issue valid discard ranges plus parallel random discards, verify readonly rejection, and require invalid ranges/unaligned requests to fail. State includes real target block contents and read-only setting, so integration is through the test runner's configured device map. Main risks are data destruction, privilege/device availability, unsupported discard, and false results from unsuitable targets.
