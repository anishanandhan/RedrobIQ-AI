import sys
import pytest
from unittest.mock import patch
from rank import main

def test_cli_help():
    # Verify running with --help exits with code 0 or prints help
    with patch.object(sys, "argv", ["rank.py", "--help"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

def test_cli_missing_args():
    # Verify missing required args exits with code 2 (argument error)
    with patch.object(sys, "argv", ["rank.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

def test_cli_file_not_found():
    # Verify file not found exits with code 1
    with patch.object(sys, "argv", ["rank.py", "--candidates", "nonexistent.jsonl", "--out", "test.csv"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
