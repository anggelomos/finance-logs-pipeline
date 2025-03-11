"""Tests for the configuration module."""

from pathlib import Path


from finance_logs_pipeline.config import AppConfig, config


def test_config_loads():
    """Test that the config loads correctly."""
    assert config is not None
    assert isinstance(config, AppConfig)


def test_directories():
    """Test that directories are configured correctly."""
    assert isinstance(config.input_dir, Path)
    assert isinstance(config.archive_dir, Path)
    assert isinstance(config.logs_dir, Path)
