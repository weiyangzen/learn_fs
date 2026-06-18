# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/reliability.py

## Purpose

This module simulates erasure-coded file reliability over time using Markov transition matrices for share loss and repair.

## Important APIs, Types, and Functions

Constants define day/month/year seconds. `ReliabilityModel.run` builds and advances unmaintained and maintained probability vectors. `p_in_period` computes exponential survival probability. `build_decay_matrix` and `build_decay_row` build share-count transition probabilities using `allmydata.util.statistics.binomial_distribution_pmf`. `build_repair_matrix` models deterministic repair when shares fall below `R` but remain at least `k`. `ReliabilityReport` stores sampled rows via `add_sample`.

## Control Flow

`run` computes drive survival per delta, creates decay and repair matrices, initializes all probability at `N` shares, then iterates through simulated time. Each delta decays both states; at check periods it computes repair probability/new-share expectation and applies repair to the maintained state; at report periods it records dead probabilities and cumulative repair metrics. A final sample is always added.

## State, Dependencies, Integration, Risks, and Tests

State is the returned `ReliabilityReport.samples` list. Dependencies are NumPy and Tahoe statistics utilities. Integration is `web_reliability.py` and `test_provisioning.py`. Risks include matrix/array shape sensitivity, `check_period = check_period - 1` timing subtlety, optimistic independence assumptions, Python 2 integer behavior, and old NumPy matrix APIs. Tests should assert row counts, matrix rows sum to one, repair matrix transitions, known probability outputs, and behavior for edge k/R/N values.
