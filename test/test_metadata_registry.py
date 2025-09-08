"""
Tests for the metadata plugin registry system.

This module tests the plugin registration, discovery, and instantiation
functionality of the metadata registry.
"""

from pathlib import Path
from typing import Any, ClassVar, Optional

import pytest

from dirac_cwl_proto.metadata.core import BaseMetadataModel, DataManager
from dirac_cwl_proto.metadata.registry import (
    MetadataPluginRegistry,
    get_registry,
)


class TestPluginMetadata(BaseMetadataModel):
    """Test plugin for registry testing."""

    description: ClassVar[str] = "Test plugin for unit tests"

    test_param: str = "default"


class TestVOPlugin(BaseMetadataModel):
    """Test vo-specific plugin."""

    description: ClassVar[str] = "Test VO plugin"
    vo: ClassVar[Optional[str]] = "test_exp"

    exp_param: int = 42


class TestSecondVOPlugin(BaseMetadataModel):
    """Test plugin for second vo."""

    description: ClassVar[str] = "Test plugin for second VO"
    vo: ClassVar[Optional[str]] = "exp2"

    param2: str = "test"


class TestMetadataPluginRegistry:
    """Test the MetadataPluginRegistry class."""

    def test_creation(self):
        """Test registry creation."""
        registry = MetadataPluginRegistry()
        assert len(registry.list_plugins()) == 0
        assert len(registry.list_virtual_organizations()) == 0

    def test_register_plugin(self):
        """Test plugin registration."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)

        plugins = registry.list_plugins()
        assert "TestPlugin" in plugins
        assert len(plugins) == 1

    def test_register_plugin_with_vo(self):
        """Test vo-specific plugin registration."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestVOPlugin)

        plugins = registry.list_plugins()
        assert "TestVOPlugin" in plugins

        vos = registry.list_virtual_organizations()
        assert "test_exp" in vos

        exp_plugins = registry.list_plugins(vo="test_exp")
        assert "TestVOPlugin" in exp_plugins

    def test_register_duplicate_plugin(self):
        """Test that duplicate registration raises error."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)

        # Should raise error without override
        with pytest.raises(ValueError, match="already registered"):
            registry.register_plugin(TestPluginMetadata)

    def test_register_duplicate_plugin_with_override(self):
        """Test that duplicate registration works with override."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)
        registry.register_plugin(TestPluginMetadata, override=True)

        # Should not raise error with override=True
        plugins = registry.list_plugins()
        assert "TestPlugin" in plugins

    def test_get_plugin(self):
        """Test getting registered plugin."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)

        plugin_class = registry.get_plugin("TestPlugin")
        assert plugin_class is TestPluginMetadata

    def test_get_nonexistent_plugin(self):
        """Test getting non-existent plugin."""
        registry = MetadataPluginRegistry()

        plugin = registry.get_plugin("NonExistent")
        assert plugin is None

    def test_get_plugin_with_vo(self):
        """Test getting vo-specific plugin."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestVOPlugin)

        plugin_class = registry.get_plugin("TestVOPlugin", vo="test_exp")
        assert plugin_class is TestVOPlugin

    def test_instantiate_plugin(self):
        """Test plugin instantiation."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)

        descriptor = DataManager(metadata_class="TestPlugin", test_param="custom")
        instance = registry.instantiate_plugin(descriptor)

        assert isinstance(instance, TestPluginMetadata)
        assert instance.test_param == "custom"

    def test_instantiate_plugin_with_vo(self):
        """Test vo plugin instantiation."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestVOPlugin)

        descriptor = DataManager(
            metadata_class="TestVOPlugin", vo="test_exp", exp_param=99
        )
        instance = registry.instantiate_plugin(descriptor)

        assert isinstance(instance, TestVOPlugin)
        assert instance.exp_param == 99

    def test_instantiate_nonexistent_plugin(self):
        """Test instantiation of non-existent plugin."""
        registry = MetadataPluginRegistry()

        descriptor = DataManager(metadata_class="NonExistent")

        with pytest.raises(KeyError, match="Unknown metadata plugin"):
            registry.instantiate_plugin(descriptor)

    def test_discover_plugins(self):
        """Test automatic plugin discovery."""
        registry = MetadataPluginRegistry()

        # Test discovery from a package that doesn't exist - should return 0
        discovered = registry.discover_plugins(["nonexistent.package"])
        assert discovered == 0

        # Test that the registry still works normally
        plugins = registry.list_plugins()
        assert isinstance(plugins, list)

    def test_list_virtual_organizations(self):
        """Test listing vos."""
        registry = MetadataPluginRegistry()

        assert len(registry.list_virtual_organizations()) == 0

        registry.register_plugin(TestVOPlugin)  # exp1 = test_exp
        registry.register_plugin(TestSecondVOPlugin)  # exp2

        vos = registry.list_virtual_organizations()
        assert "test_exp" in vos
        assert "exp2" in vos
        assert len(vos) == 2

    def test_list_plugins_by_vo(self):
        """Test listing plugins by vo."""
        registry = MetadataPluginRegistry()

        registry.register_plugin(TestPluginMetadata)  # No vo
        registry.register_plugin(TestVOPlugin)  # test_exp vo

        # All plugins
        all_plugins = registry.list_plugins()
        assert "TestPlugin" in all_plugins
        assert "TestVOPlugin" in all_plugins

        # vo-specific plugins
        exp_plugins = registry.list_plugins(vo="test_exp")
        assert "TestVOPlugin" in exp_plugins
        assert "TestPlugin" not in exp_plugins


class TestGlobalRegistryFunctions:
    """Test the global registry functions."""

    def test_get_registry(self):
        """Test getting the global registry."""
        registry = get_registry()
        assert isinstance(registry, MetadataPluginRegistry)

        # Should return the same instance
        registry2 = get_registry()
        assert registry is registry2


class TestPluginSystem:
    """Test the modern plugin system functionality."""

    def test_direct_plugin_usage(self):
        """Test using plugins directly without legacy wrapper."""
        from dirac_cwl_proto.metadata.core import BaseMetadataModel

        class DirectPlugin(BaseMetadataModel):
            test_param: str = "default"

            def get_input_query(self, input_name: str, **kwargs: Any) -> Optional[Path]:
                return Path(f"/direct/{input_name}/{self.test_param}")

        # Register plugin directly
        registry = get_registry()
        registry.register_plugin(DirectPlugin)

        # Should be able to instantiate
        descriptor = DataManager(metadata_class="DirectPlugin", test_param="custom")
        instance = registry.instantiate_plugin(descriptor)

        # Should work with new interface
        result = instance.get_input_query("test_input")
        assert result == Path("/direct/test_input/custom")

    def test_plugin_parameter_handling(self):
        """Test that parameters are passed correctly to plugins."""
        from dirac_cwl_proto.metadata.core import BaseMetadataModel

        class ParameterTestPlugin(BaseMetadataModel):
            test_param: str = "default"
            another_param: str = "default"

        registry = get_registry()
        registry.register_plugin(ParameterTestPlugin)

        # Test with snake_case parameters (should work)
        descriptor = DataManager(
            metadata_class="ParameterTestPlugin",
            test_param="value1",
            another_param="value2",
        )
        instance = registry.instantiate_plugin(descriptor)

        assert instance.test_param == "value1"
        assert instance.another_param == "value2"
