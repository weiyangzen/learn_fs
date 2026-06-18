# sources/test-tools/syzkaller/sys/syz-extract/trusty.go

Purpose: Trusty OS backend for extracting constants from Trusty/LK headers.

Important APIs/types/functions: `trusty.prepare`, `trusty.prepareArch`, and `trusty.processFile`.

Control flow: prepare hooks are no-ops. `processFile` adds LK shared and Trusty user base include paths, any syzlang-requested include dirs, optional external include dirs, then invokes shared extraction via `gcc`.

State and persistence: only temporary compiler artifacts.

Dependencies and integration points: depends on Trusty source layout and the shared `extract` engine.

Risks: minimal backend assumes GCC and a fixed include structure; no build validation is done before compilation.

Test signals: no direct tests in this subset.
