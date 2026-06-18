<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/mtd.c -->
# sources/test-tools/strace/attic/test/mtd.c

Purpose: ioctl decoder exerciser for MTD user API structures and commands.

Important data/types: declares `mtd_info_user`, erase info 32/64, OOB buffers 32/64, region info, ECC stats, write request, NAND OOB info, and NAND ECC layout. Issues `MEMGETINFO`, `MEMERASE`, `MEMERASE64`, bad-block, OTP, OOB, region, ECC, and write ioctls against `/dev/null`.

Control flow: initializes selected structures, opens `/dev/null`, then sends a fixed sequence of ioctl calls.

State and persistence: no intended device changes because fd is `/dev/null`; the observable state is syscall arguments.

Dependencies and integration: requires `<mtd/mtd-user.h>` and strace MTD ioctl decoders.

Risks: header availability varies by system. Uninitialized structures are intentional for decoder coverage but can produce nondeterministic bytes. Test signals: strace should decode each MTD ioctl name and structure fields rather than only raw numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/mtd.c -->
