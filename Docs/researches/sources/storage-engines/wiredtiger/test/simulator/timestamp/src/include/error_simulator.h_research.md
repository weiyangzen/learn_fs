# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/error_simulator.h

Purpose: small error/return macro header for the timestamp simulator, mirroring common WiredTiger-style early-return patterns.

Important APIs and control flow: `WT_SIM_RET` and `WT_SIM_RET_MSG` evaluate an expression and return nonzero errors, optionally printing a message. `WT_TXN_SIM_RET` and `WT_TXN_SIM_RET_MSG` additionally set `_txn_error = true` before returning, intended for methods inside `session_simulator`. The header defines `EINVAL` as 22.

State and persistence behavior: macros do not own state, but transaction variants mutate the caller's `_txn_error` member.

Dependencies and integration points: assumes `std::cerr` is available where message macros are used and that transaction macros are expanded in a class scope with `_txn_error`.

Risks: macro hygiene is limited; transaction macros are not safe outside `session_simulator`. Defining `EINVAL` can conflict with system errno headers if included together.

Test signals: validation failures should return 22 and, for transaction timestamp errors, cause later commit to roll back.
