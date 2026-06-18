# sources/test-tools/stress-ng/stress-sigpipe.c

Purpose: implements the `sigpipe` stressor, repeatedly writing to a pipe with the read end closed to generate EPIPE and SIGPIPE.

Important APIs/types/functions: `stress_sigpipe_handler_count_check`, `stress_sigpipe`, `pipe`, `write`, `close`, `stress_signal_handler`, `stress_signal_ignore_handler`, and `stress_bogo_inc`.

Control flow: the worker installs a SIGPIPE handler that increments bogo ops when max-ops is set, otherwise ignores SIGPIPE. It creates a pipe, closes the read end, synchronizes start, loops writing one byte to the write end, counts EPIPE errors, and after stopping verifies that repeated EPIPEs corresponded to at least one handled SIGPIPE.

State and persistence behavior: state is one pipe fd pair and a global args pointer. The write fd is closed at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on stress-ng signal helpers and pipe semantics.

Risks and test signals: if SIGPIPE is ignored or coalesced unexpectedly, bogo count may stay zero despite EPIPE. Failures include pipe creation failure, missing SIGPIPE delivery, or fd cleanup issues.
