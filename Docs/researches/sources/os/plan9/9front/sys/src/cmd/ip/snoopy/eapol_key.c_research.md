# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol_key.c

This module decodes EAPOL-Key descriptor selection and the RC4 key descriptor subtype.

The top-level `eapol_key` protocol reads a one-byte descriptor and demuxes descriptor type 1 to `rc4keydesc`. It prints the descriptor name.

`p_seprintrc4` consumes the RC4 key descriptor fields: key length, replay counter, IV, key index, MIC/digest, and remaining key data. It prints these values and any trailing data as hex.

Some multi-byte fields such as replay, IV, and digest are wider than `NetS`, so the printed numeric summaries are abbreviated rather than full-field decodes.
