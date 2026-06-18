# sources/storage-engines/tikv/codecov.yml

## Purpose
`codecov.yml` configures Codecov reporting thresholds, comment layout, flag carryforward, and ignored paths for the TiKV source tree.

## Important APIs, Types, And Functions
This is YAML configuration. It sets coverage precision to 4, rounds down, displays a `65...90` range, and uses automatic project/patch targets with a 3% threshold. It also defines default flag-management rules requiring 85% project and patch coverage for flags.

## Control Flow
Codecov consumes this file during coverage upload/reporting. Pull request comments use `header, diff, flags`, default behavior, and do not require changes to post.

## State And Persistence Behavior
No runtime state is affected. The file affects CI status interpretation and PR feedback.

## Dependencies And Integration Points
It integrates with Codecov CI uploads and path layout. Ignored paths include integration tests/tools, fuzz cases, test components, component test crates, and component-local `tests` directories.

## Risks And Edge Cases
- Ignoring test directories can make source coverage easier to interpret but hides coverage of test utilities.
- Automatic targets with thresholds may allow coverage drops within 3%.
- Carryforward can mask missing uploads for a flag if not monitored separately.

## Test Signals
The signal is Codecov status output in CI. Changes to source layout should be checked against the ignore globs.
