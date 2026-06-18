# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_statistics.py

## Purpose
This module tests probability and repair-cost helpers in `allmydata.util.statistics`. The covered functions model binomial probabilities, survival distributions, convolution, repair counts, repair costs, and threshold selection for erasure-coded file-loss risk.

## Important APIs, Types, And Functions
The `Statistics` test case defines small assertion helpers: `should_assert` expects an `AssertionError`, `failUnlessListEqual` compares exact lists element by element, and `failUnlessListAlmostEqual` compares floating-point lists. Tested production APIs include `binomial_coeff`, `binomial_distribution_pmf`, `print_pmf`, `survival_pmf`, `survival_pmf_via_conv`, `survival_pmf_via_bd`, `valid_pmf`, `repair_count_pmf`, `bandwidth_cost_function`, `mean_repair_cost`, `eternal_repair_cost`, `convolve`, `find_k`, `pr_file_loss`, and `pr_backup_file_loss`.

## Control Flow
Each test focuses on one mathematical contract. Binomial coefficient checks base cases, symmetry, and invalid `n < k`. Binomial PMF tests known values for `n=2, p=.1`, total probability near one, input assertions, and text output from `print_pmf`. Survival PMF cross-checks two independent implementations, convolution and binomial-distribution grouping, over a mixed reliability vector.

Repair tests build a survival PMF from five servers at `.9`, transform it with `repair_count_pmf(k=3)`, and verify the exact mapping of lost/surviving-share counts to repair counts. Cost tests feed the same PMF into mean and eternal repair-cost functions with different upload/download ratios and discount rates. Convolution tests algebraic properties: commutativity, associativity, distributivity, and scalar-multiplication associativity. The final tests verify `find_k` selects a threshold under a target loss probability and that file-loss helpers return known values for homogeneous reliabilities.

## State And Persistence Behavior
There is no persistent state. All tested functions operate on numeric inputs and return numbers or lists. The only side effect is `print_pmf`, which writes formatted lines to a provided `StringIO` object. Floating-point state is validated with approximate equality where appropriate.

## Dependencies And Integration Points
The module depends on Twisted Trial, `io.StringIO`, and `allmydata.util.statistics`. These helpers feed Tahoe-LAFS reasoning around share survival, file loss probability, and expected repair bandwidth, so correctness matters for capacity planning and reliability modeling rather than direct protocol behavior.

## Risks And Edge Cases
The tests cover invalid probabilities outside `[0, 1]`, invalid sample counts, coefficient symmetry, PMF normalization, and cross-implementation agreement. Some expected cost values are acknowledged in comments as not manually checked beyond a point, so they act as regression fixtures more than independently derived proofs. Floating-point tolerance must remain stable if algorithms are refactored.

## Test Signals
Passing tests signal that probability distributions remain normalized and consistent, convolution behaves algebraically, repair-count and cost helpers preserve historical outputs, and `find_k` can choose an erasure-coding threshold that keeps modeled file-loss probability below a target.
