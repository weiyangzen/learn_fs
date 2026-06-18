<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.c -->
# sources/security-integrity/selinux/libsepol/tests/test-neverallow.c

## Purpose

CUnit suite for neverallow and neverallowxperm assertion diagnostics. It builds several policy fixtures, expands them, runs `check_assertions()`, captures libsepol messages through a custom callback, and compares exact expected failure output. The source was read completely for this report (393 lines).

## Important APIs, Types, and Functions

`msg_handler()` stores formatted sepol messages in a linked list. `messages_check()` compares count and message text. Test cases cover basic neverallow, minus self, not self, and conditional neverallow scenarios. `neverallow_add_tests()` skips the suite under MLS mode and registers the four cases otherwise.

## Control Flow

Each test initializes policydbs, loads a fixture, links and expands it, installs the message callback on a `sepol_handle_t`, expects `check_assertions()` to fail, checks all messages, then destroys handle, messages, and policydbs.

## State and Persistence Behavior

State consists of a temporary linked list of captured messages and per-test policydb/handle objects. No persistent files are changed.

## Dependencies and Integration Points

Depends on libsepol debug/link/expand assertion APIs, local policy fixtures in `policies/test-neverallow`, GNU `vasprintf`, and CUnit.

## Risks and Edge Cases

Exact string expectations are intentionally brittle: line-number or wording changes require fixture/test updates. The list insertion order also depends on libsepol callback ordering.

## Test Signals

Strong signal for assertion matching, xperm diagnostics, self-set handling, conditional assertion evaluation, and user-visible error text.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.c -->
