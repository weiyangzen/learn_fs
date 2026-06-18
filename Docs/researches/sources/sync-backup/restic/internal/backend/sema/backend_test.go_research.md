<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend_test.go -->
# sources/sync-backup/restic/internal/backend/sema/backend_test.go

## Purpose
Tests connection-limiting backend validation, concurrency, lock-file exemptions, freeze/unfreeze, and unwrapping.

## Important APIs, Types, And Functions
Tests include parameter validation for Save/Load/Stat/Remove, concurrencyTester helpers, and freeze behavior.

## Control Flow
Mock backends block in callbacks while goroutines count how many operations enter concurrently. Tests compare against configured connection counts and lock-file unlimited behavior.

## State And Persistence Behavior
No persistence; synchronization state is in test goroutines/channels.

## Dependencies And Integration Points
Depends on mock backend, errgroup, atomics, context, and internal/test assertions.

## Risks And Edge Cases
Concurrency tests rely on small sleeps/polling but avoid precise timing for throughput.

## Test Signals
Strong signal for wrapper correctness under parallel access.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend_test.go -->
