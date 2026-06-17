```markdown
# Vintage-Tel-with-Bluetooth Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill covers the development patterns and conventions used in the `Vintage-Tel-with-Bluetooth` repository, a Python-based project that adds Bluetooth functionality to vintage telephones. It documents coding standards, commit practices, testing approaches, and common workflows to help contributors maintain consistency and quality.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `bluetooth_adapter.py`, `test_utils.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_signal
    ```

### Export Style
- Use **named exports** (i.e., define and import specific functions/classes).
  - Example:
    ```python
    # In bluetooth_adapter.py
    def connect_device(...):
        ...
    # In another file
    from .bluetooth_adapter import connect_device
    ```

### Commit Messages
- Follow **conventional commit** format.
- Prefixes: `fix`, `test`
- Example:
  ```
  fix: resolve pairing issue with legacy handsets
  test: add tests for dial pulse decoding
  ```

## Workflows

### Feature Implementation with Tests
**Trigger:** When adding a new feature or fixing a bug and ensuring it is covered by tests.  
**Command:** `/feature-with-tests`

1. **Modify or add implementation files** in `firmware/src/`.
    - Example: Edit `firmware/src/bluetooth_adapter.py` to add a new pairing method.
2. **Create or update test files** in `firmware/tests/` to cover the new or changed functionality.
    - Example: Add `firmware/tests/test_bluetooth_adapter.py` with tests for the new method.
3. **Update configuration or example files** if needed (e.g., `config.example.yaml`).
4. **Commit both the implementation and tests together** using a conventional commit message.
    - Example:
      ```
      fix: add support for Bluetooth 5.0 devices
      test: add tests for Bluetooth 5.0 compatibility
      ```

#### Example Directory Structure
```
firmware/
  src/
    bluetooth_adapter.py
    utils.py
  tests/
    test_bluetooth_adapter.py
    test_utils.py
```

## Testing Patterns

- **Test files** are located in `firmware/tests/` and named with the pattern `test_*.py`.
- **Testing framework** is not explicitly specified; use standard Python `unittest` or `pytest` conventions.
- Each test file targets a corresponding module in `firmware/src/`.
- Example test file:
    ```python
    # firmware/tests/test_bluetooth_adapter.py
    import unittest
    from ..src.bluetooth_adapter import connect_device

    class TestBluetoothAdapter(unittest.TestCase):
        def test_connect_device_success(self):
            self.assertTrue(connect_device("00:11:22:33:44:55"))
    ```

## Commands

| Command              | Purpose                                                         |
|----------------------|-----------------------------------------------------------------|
| /feature-with-tests  | Start a new feature or bugfix with corresponding tests          |
```
