# sources/security-integrity/selinux/libsepol/cil/test/integration_testing/nonmls.conf

## Purpose
`nonmls.conf` is a compact non-MLS SELinux policy fixture used by integration tests. It exercises baseline declarations and rules without MLS level/range syntax.

## Important Declarations
The fixture declares `class testing` and `class fooclass`, `sid test_sid` and `sid security`, permission sets for both classes, one attribute `attrs`, types `foo_t`, `typea_t`, `typeb_t`, and `typec_t`, booleans `foo_b` and `baz_b`, roles `foo_r`, `rolea_r`, and `roleb_r`, allow rules, a `type_transition`, a role allow, user `foo_u`, and a final SID context `foo_u:foo_r:foo_t`.

## Control Flow
This is declarative policy input, not procedural code. The integration test flow parses this file, translates declarations and rules into CIL/policy structures, and checks that a minimal non-MLS policy can be accepted.

## State And Persistence
The file is static test data. Its state is the policy text persisted in the repository. The test harness reads it as input and does not update it.

## Dependencies And Integration Points
It depends on the legacy policy syntax expected by the integration pipeline. It integrates with the CIL integration test fixtures under `test/integration_testing` and with test registrations from `CilTestFullCil()`.

## Risks
Because this fixture intentionally omits MLS details, it cannot catch MLS serializer/resolver regressions. It also contains commented-out examples and section markers such as `#end`, so tests must treat comments as comments and not assume every visible line is active policy. Any parser syntax change affecting non-MLS policy declarations, allow rules, role rules, or SID contexts may break this fixture.

## Test Signals
A passing integration run using this fixture signals that basic class, SID, type, attribute, bool, role, allow, type transition, user, and SID context handling still works for non-MLS input.
