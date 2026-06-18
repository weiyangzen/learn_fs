<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_azure.go -->
# sources/sync-backup/kopia/cli/storage_azure.go

## Purpose
Implements CLI flags and connection creation for Azure Blob Storage repositories.

## Important APIs, Types, And Functions
Defines `storageAzureFlags`, `Setup`, `Connect`, and `init` registration. It fills `azure.Options` with container, account, key/SAS/service-principal/federated-token fields, prefix, throttling limits, storage domain, and optional point-in-time.

## Control Flow
Setup binds flags and parses point-in-time in a pre-action. Connect rejects point-in-time on repository creation and calls `azure.New`.

## State And Persistence Behavior
Persistent state is backend configuration stored by repository connect/create code outside this file. This file constructs transient option structs and may embed credential values from flags/environment.

## Dependencies And Integration Points
Integrates storage provider registry, Kingpin, Azure blob backend, throttling flags, and env-name namespacing.

## Risks And Edge Cases
Credential combinations are mostly validated by the backend. Point-in-time format must be RFC3339 and is read-only only. Sensitive credentials can be present in process args/env.

## Test Signals
Tests should cover required flags, env overrides, point-in-time parsing/rejection on create, throttling propagation, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_azure.go -->
