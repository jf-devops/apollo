#!/usr/bin/env python3
"""
Detailed anyio debugging script
"""
import sys
import os
import importlib.util

def inspect_anyio_structure():
    print("=== anyio Module Structure ===")
    
    try:
        import anyio
        print(f"anyio version: {anyio.__version__}")
        print(f"anyio location: {anyio.__file__}")
        
        # Check if _core exists
        if hasattr(anyio, '_core'):
            print("✅ anyio._core exists")
            
            # Check if _exceptions exists
            if hasattr(anyio._core, '_exceptions'):
                print("✅ anyio._core._exceptions exists")
                
                # List all attributes in _exceptions
                exceptions_attrs = dir(anyio._core._exceptions)
                print(f"Attributes in _exceptions: {exceptions_attrs}")
                
                if 'ExceptionGroup' in exceptions_attrs:
                    print("✅ ExceptionGroup found in _exceptions")
                else:
                    print("❌ ExceptionGroup NOT found in _exceptions")
            else:
                print("❌ anyio._core._exceptions does not exist")
        else:
            print("❌ anyio._core does not exist")
            
        # Check _backends
        if hasattr(anyio, '_backends'):
            print("✅ anyio._backends exists")
            
            if hasattr(anyio._backends, '_asyncio'):
                print("✅ anyio._backends._asyncio exists")
                
                # Try to import the problematic module
                try:
                    asyncio_module = importlib.import_module('anyio._backends._asyncio')
                    print(f"✅ Successfully imported anyio._backends._asyncio")
                    
                    # Check the source code around line 61
                    asyncio_file = asyncio_module.__file__
                    if os.path.exists(asyncio_file):
                        with open(asyncio_file, 'r') as f:
                            lines = f.readlines()
                            if len(lines) >= 61:
                                print(f"Line 61: {lines[60].strip()}")
                            else:
                                print(f"File has {len(lines)} lines, line 61 doesn't exist")
                except Exception as e:
                    print(f"❌ Error importing _asyncio: {e}")
            else:
                print("❌ anyio._backends._asyncio does not exist")
        else:
            print("❌ anyio._backends does not exist")
            
    except Exception as e:
        print(f"❌ Error inspecting anyio: {e}")

def test_python_version_compatibility():
    print("\n=== Python Version Compatibility ===")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    # Check if ExceptionGroup is available in builtins
    try:
        from builtins import ExceptionGroup
        print("✅ ExceptionGroup available in builtins")
    except ImportError:
        print("❌ ExceptionGroup not available in builtins")
        
        # Try importing from typing
        try:
            from typing import ExceptionGroup
            print("✅ ExceptionGroup available in typing")
        except ImportError:
            print("❌ ExceptionGroup not available in typing")

def test_alternative_imports():
    print("\n=== Alternative Import Tests ===")
    
    # Test different ways to import ExceptionGroup
    import_methods = [
        ("builtins", "ExceptionGroup"),
        ("typing", "ExceptionGroup"),
        ("anyio._core._exceptions", "ExceptionGroup"),
        ("anyio._backends._asyncio", "ExceptionGroup"),
    ]
    
    for module, name in import_methods:
        try:
            if module == "builtins":
                from builtins import ExceptionGroup
            elif module == "typing":
                from typing import ExceptionGroup
            else:
                # Dynamic import
                mod = importlib.import_module(module)
                ExceptionGroup = getattr(mod, name)
            print(f"✅ Successfully imported {name} from {module}")
        except Exception as e:
            print(f"❌ Failed to import {name} from {module}: {e}")

if __name__ == "__main__":
    print("Starting detailed anyio debug...")
    
    inspect_anyio_structure()
    test_python_version_compatibility()
    test_alternative_imports()
    
    print("\n=== Debug Complete ===") 