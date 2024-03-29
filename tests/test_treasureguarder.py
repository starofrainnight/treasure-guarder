#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `treasure-guarder` package."""

from click.testing import CliRunner
from treasureguarder.__main__ import main


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    help_result = runner.invoke(main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
