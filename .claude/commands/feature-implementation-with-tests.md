---
name: feature-implementation-with-tests
description: Workflow command scaffold for feature-implementation-with-tests in Vintage-Tel-with-Bluetooth.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-implementation-with-tests

Use this workflow when working on **feature-implementation-with-tests** in `Vintage-Tel-with-Bluetooth`.

## Goal

Implements or fixes a feature in the core firmware and adds/updates corresponding tests to ensure correctness.

## Common Files

- `firmware/src/*.py`
- `firmware/tests/test_*.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Modify or add implementation files in firmware/src/
- Create or update test files in firmware/tests/ to cover the new or changed functionality
- Update configuration or example files if needed (e.g., config.example.yaml)
- Commit both the implementation and tests together

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.