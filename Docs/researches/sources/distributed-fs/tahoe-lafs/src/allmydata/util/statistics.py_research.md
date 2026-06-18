# sources/distributed-fs/tahoe-lafs/src/allmydata/util/statistics.py

## Purpose

This module computes probability mass functions and repair cost estimates for erasure-coded file survival. It assumes independent share/server survival probabilities and helps reason about `k-of-N` reliability and repair economics.

## APIs and control flow

`pr_file_loss()` sums survival PMF entries below `k`. `survival_pmf()` validates probabilities and uses convolution over `[1-p, p]` terms; `survival_pmf_via_bd()` is an internal/test alternative grouped by equal probabilities. `pr_backup_file_loss()` factors in source survival. `find_k()` and `find_k_from_pmf()` choose the highest recoverability threshold meeting a target loss probability. `repair_count_pmf()`, `bandwidth_cost_function()`, `mean_repair_cost()`, and `eternal_repair_cost()` estimate repair distributions and long-term costs. Validation and math helpers include `valid_pmf`, `valid_probability_list`, `convolve`, `binomial_distribution_pmf`, and `binomial_coeff`.

## State, dependencies, risks, and tests

There is no persistent state. Dependencies are `math`, `functools.reduce`, `sys.stdout`, and `mathutil.round_sigfigs`. Integration is analytical/planning code rather than live storage mutation.

Risks include the independence assumption being invalid for co-located shares, floating-point rounding in `valid_pmf`, binomial path limitations, and ambiguous `find_k` wording versus loop behavior. Test signals should compare convolution/binomial PMFs for small cases, validate edge probabilities 0/1, loss probability boundaries, repair PMF validity, cost formulas, printed PMFs, and invalid probability inputs.
