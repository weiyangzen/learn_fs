# sources/user-network-fs/mergerfs/src/policy_rand.cpp

## Purpose
Implements the `rand` policy by delegating to existing eligible-branch policies and shrinking successful results to a single random branch.

## Important APIs, Types, and Functions
`Policy::Rand::{Action,Create,Search}::operator()` call `Policies::Action::all`, `Policies::Create::all`, and `Policies::Search::all`, then use `RND::shrink_to_rand_elem(paths_)` when the helper returns success.

## Control Flow
The policy first gathers all eligible branches for the operation category. If the shared helper fails, it returns that error. If it succeeds and multiple branches were returned, a random element is swapped to the front and the vector is resized to one.

## State and Persistence Behavior
The file is stateless but consumes the process-global RNG seed. Persistence is determined by the caller that acts on the selected branch.

## Dependencies and Integration Points
It depends on `policies.hpp`, `policy_rand.hpp`, and `rnd.hpp`. It composes with the broader policy framework rather than reimplementing branch eligibility.

## Risks and Edge Cases
Random choice is not cryptographic and is modulo-based. Eligibility depends entirely on `all` helpers, so changes there alter `rand` behavior. Multi-branch operations that expected all outputs must not use this policy.

## Test Signals
Test single and multiple eligible branches, helper failure propagation, distribution across repeated runs, and create/action/search category differences.
