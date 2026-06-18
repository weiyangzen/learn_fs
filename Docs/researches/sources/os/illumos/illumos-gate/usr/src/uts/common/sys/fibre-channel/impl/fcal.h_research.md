# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcal.h

Defines FC-AL loop initialization identifiers and magic values for LISM, LIFA, LIPA, LIHA, LISA, LIRP, and LILP. It also defines PLDA timer values and `LILP_LBIT_SET`, which signals login-required state in the high bits of `lilp_myalpa`.

The main structure is `fc_lilpmap_t`, containing the loop initialization map magic, local AL_PA, map length, and up to 127 AL_PA entries. This is consumed by fp/fctl loop discovery and private loop diagnostics.

This header is small but wire/protocol significant: the AL_PA list and LBIT behavior influence whether fp performs implicit logout and PLOGI after loop initialization.
