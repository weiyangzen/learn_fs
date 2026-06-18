# File Research: sources/os/linux/linux/fs/dlm/requestqueue.h

## Role

`requestqueue.h` declares requestqueue operations.

## Interface

It exposes add, process, wait, and purge functions for saved recovery-time messages.

## Research Notes

Read completely. `dlm_wait_requestqueue()` is declared here but implemented outside this file group.
