# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/test_provisioning.py

## Purpose

This unittest module smoke-tests the provisioning calculator and reliability model.

## Important APIs, Types, and Functions

`Provisioning.getarg` reads values from `self.fields`. `test_load` calls `ProvisioningTool.do_forms` with empty and filled fields, including server wraparound and ownership modes. `test_provisioning_math` verifies selected binomial outputs. `Reliability.test_basic` checks NumPy vector/matrix multiplication, dot products, runs `ReliabilityModel`, and asserts known final probabilities.

## Control Flow

Reliability tests are skipped if the NumPy-backed model cannot be imported. Otherwise tests run under stdlib unittest and can be executed directly.

## State, Dependencies, Integration, Risks, and Tests

State is per-test `self.fields`. Dependencies are old import names `allmydata.provisioning` and `allmydata.reliability`, Nevow interface imports, NumPy, and unittest. Risks include tests importing modules from package locations different from the misc directory, Python 2 unittest methods (`failUnless*`), and brittle floating expected values. These tests themselves are the strongest signal for calculator smoke coverage but do not validate rendered HTML content or many invalid inputs.
