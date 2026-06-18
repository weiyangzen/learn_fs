# sources/user-network-fs/rclone/cmd/serve/ftp/ftp_unsupported.go

## Purpose

This Plan 9 fallback prevents package build errors where FTP serving is unsupported.

## Important APIs, Types, and Functions

It defines `var Command *cobra.Command` as nil.

## Control Flow

No command is registered from this file. The nil command marks the feature unavailable on Plan 9.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `plan9`. It imports Cobra only for the command type.

## Risks and Test Signals

The main risk is callers assuming `ftp.Command` is non-nil on all platforms. Platform compile coverage is the test signal.
